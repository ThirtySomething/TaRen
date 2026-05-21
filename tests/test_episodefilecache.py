import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from taren.episodefilecache import EpisodeFileCache


class TestEpisodeFileCache(unittest.TestCase):
    def test_initialize_creates_sqlite_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = str(Path(tmpdir) / "episodes.sqlite3")
            cache = EpisodeFileCache(db_path)

            cache.initialize()

            with sqlite3.connect(db_path) as conn:
                rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='episode_file_cache'").fetchall()
            self.assertEqual(len(rows), 1)

    def test_reconcile_tracks_manual_move_downloads_to_seen(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            downloads = root / "downloads"
            seen = root / "seen"
            unseen = root / "unseen"
            downloads.mkdir()
            seen.mkdir()
            unseen.mkdir()

            file_in_downloads = downloads / "Tatort_test.mp4"
            file_in_downloads.write_bytes(b"abc123")

            db_path = str(root / "episodes.sqlite3")
            cache = EpisodeFileCache(db_path)
            cache.initialize()
            cache.reconcile(str(downloads), str(seen), str(unseen), ".mp4")

            moved_path = seen / file_in_downloads.name
            file_in_downloads.rename(moved_path)
            cache.reconcile(str(downloads), str(seen), str(unseen), ".mp4")

            with sqlite3.connect(db_path) as conn:
                rows = conn.execute("SELECT path, folder_state FROM episode_file_cache ORDER BY id").fetchall()

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][0], str(moved_path.resolve()))
            self.assertEqual(rows[0][1], "seen")

    def test_reconcile_marks_missing_when_file_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            downloads = root / "downloads"
            seen = root / "seen"
            unseen = root / "unseen"
            downloads.mkdir()
            seen.mkdir()
            unseen.mkdir()

            cache_file = downloads / "Tatort_delete_me.mp4"
            cache_file.write_bytes(b"abc123")

            db_path = str(root / "episodes.sqlite3")
            cache = EpisodeFileCache(db_path)
            cache.initialize()
            cache.reconcile(str(downloads), str(seen), str(unseen), ".mp4")

            cache_file.unlink()
            cache.reconcile(str(downloads), str(seen), str(unseen), ".mp4")

            with sqlite3.connect(db_path) as conn:
                state = conn.execute("SELECT folder_state FROM episode_file_cache LIMIT 1").fetchone()

            self.assertIsNotNone(state)
            self.assertEqual(state[0], "missing")

    def test_find_existing_by_fingerprint_logs_database_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = EpisodeFileCache(str(Path(tmpdir) / "episodes.sqlite3"))

            with (
                patch("taren.episodefilecache.sqlite3.connect", side_effect=sqlite3.DatabaseError("db offline")),
                patch("taren.episodefilecache.logger.warning") as warning_log,
            ):
                result = cache.find_existing_by_fingerprint("abc", 123)

            self.assertIsNone(result)
            warning_log.assert_called_once()

    def test_fingerprint_small_file_is_deterministic(self) -> None:
        """Files smaller than 64 KB produce a consistent SHA-1 based on size + content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "small.mp4"
            p.write_bytes(b"hello world")

            cache = EpisodeFileCache(str(Path(tmpdir) / "episodes.sqlite3"))
            fp1 = cache._fingerprint(p, p.stat().st_size)
            fp2 = cache._fingerprint(p, p.stat().st_size)

            self.assertEqual(fp1, fp2)
            self.assertEqual(len(fp1), 40)  # SHA-1 hex digest length

    def test_fingerprint_differs_for_different_content(self) -> None:
        """Two files with the same size but different content get different fingerprints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            a = Path(tmpdir) / "a.mp4"
            b = Path(tmpdir) / "b.mp4"
            a.write_bytes(b"AAAA")
            b.write_bytes(b"BBBB")

            cache = EpisodeFileCache(str(Path(tmpdir) / "episodes.sqlite3"))
            self.assertNotEqual(
                cache._fingerprint(a, a.stat().st_size),
                cache._fingerprint(b, b.stat().st_size),
            )

    def test_fingerprint_large_file_reads_head_and_tail(self) -> None:
        """Files larger than 64 KB are fingerprinted using head + tail chunks."""
        chunk = 65536
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "large.mp4"
            # Write a file slightly larger than 64 KB with distinctive tail bytes
            data = b"\x00" * (chunk + 1)
            p.write_bytes(data)

            cache = EpisodeFileCache(str(Path(tmpdir) / "episodes.sqlite3"))
            fp = cache._fingerprint(p, len(data))

            self.assertEqual(len(fp), 40)

            # Mutate the tail; fingerprint must change
            mutated = b"\x00" * chunk + b"\xff"
            p.write_bytes(mutated)
            fp_mutated = cache._fingerprint(p, len(mutated))
            self.assertNotEqual(fp, fp_mutated)

    def test_fingerprint_large_file_same_as_small_boundary(self) -> None:
        """A file exactly at the 64 KB boundary is fingerprinted the same as a small file."""
        chunk = 65536
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "boundary.mp4"
            p.write_bytes(b"\xab" * chunk)

            cache = EpisodeFileCache(str(Path(tmpdir) / "episodes.sqlite3"))
            fp1 = cache._fingerprint(p, chunk)
            fp2 = cache._fingerprint(p, chunk)
            self.assertEqual(fp1, fp2)


if __name__ == "__main__":
    unittest.main()
