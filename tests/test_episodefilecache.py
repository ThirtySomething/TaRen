import sqlite3
import tempfile
import unittest
from pathlib import Path

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
            downloads.mkdir()
            seen.mkdir()

            file_in_downloads = downloads / "Tatort_test.mp4"
            file_in_downloads.write_bytes(b"abc123")

            db_path = str(root / "episodes.sqlite3")
            cache = EpisodeFileCache(db_path)
            cache.initialize()
            cache.reconcile(str(downloads), str(seen), ".mp4")

            moved_path = seen / file_in_downloads.name
            file_in_downloads.rename(moved_path)
            cache.reconcile(str(downloads), str(seen), ".mp4")

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
            downloads.mkdir()
            seen.mkdir()

            cache_file = downloads / "Tatort_delete_me.mp4"
            cache_file.write_bytes(b"abc123")

            db_path = str(root / "episodes.sqlite3")
            cache = EpisodeFileCache(db_path)
            cache.initialize()
            cache.reconcile(str(downloads), str(seen), ".mp4")

            cache_file.unlink()
            cache.reconcile(str(downloads), str(seen), ".mp4")

            with sqlite3.connect(db_path) as conn:
                state = conn.execute("SELECT folder_state FROM episode_file_cache LIMIT 1").fetchone()

            self.assertIsNotNone(state)
            self.assertEqual(state[0], "missing")


if __name__ == "__main__":
    unittest.main()
