import hashlib
import os
from datetime import datetime
from pathlib import Path
import sqlite3


class EpisodeFileCache:
    """SQLite-backed index of episode files discovered on disk."""

    def __init__(self, db_path: str) -> None:
        self._db_path: str = db_path

    def initialize(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS episode_file_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT NOT NULL UNIQUE,
                    folder_state TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    mtime_ns INTEGER NOT NULL,
                    dev INTEGER,
                    inode INTEGER,
                    fingerprint TEXT NOT NULL,
                    episode_id INTEGER,
                    last_seen_at TEXT NOT NULL
                )
                """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_episode_file_cache_dev_inode ON episode_file_cache(dev, inode)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_episode_file_cache_fingerprint ON episode_file_cache(fingerprint, size_bytes)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_episode_file_cache_state ON episode_file_cache(folder_state)")

    def reconcile(self, downloads_dir: str, seen_dir: str, extension: str) -> None:
        self.initialize()
        normalized_ext: str = extension if extension.startswith(".") else f".{extension}"
        observed = self._scan(downloads_dir, "downloads", normalized_ext)
        observed.extend(self._scan(seen_dir, "seen", normalized_ext))

        current_seen_marker: str = datetime.utcnow().isoformat(timespec="microseconds")
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("BEGIN")
            for row in observed:
                if self._upsert_by_inode(conn, row, current_seen_marker):
                    continue
                if self._upsert_by_fingerprint(conn, row, current_seen_marker):
                    continue
                conn.execute(
                    """
                    INSERT INTO episode_file_cache(
                        path, folder_state, size_bytes, mtime_ns, dev, inode, fingerprint, last_seen_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(path) DO UPDATE SET
                        folder_state = excluded.folder_state,
                        size_bytes = excluded.size_bytes,
                        mtime_ns = excluded.mtime_ns,
                        dev = excluded.dev,
                        inode = excluded.inode,
                        fingerprint = excluded.fingerprint,
                        last_seen_at = excluded.last_seen_at
                    """,
                    (
                        row["path"],
                        row["folder_state"],
                        row["size_bytes"],
                        row["mtime_ns"],
                        row["dev"],
                        row["inode"],
                        row["fingerprint"],
                        current_seen_marker,
                    ),
                )

            downloads_like = f"{Path(downloads_dir).resolve()}{os.sep}%"
            seen_like = f"{Path(seen_dir).resolve()}{os.sep}%"
            conn.execute(
                """
                UPDATE episode_file_cache
                SET folder_state = 'missing', last_seen_at = ?
                WHERE (path LIKE ? OR path LIKE ?)
                  AND last_seen_at <> ?
                """,
                (current_seen_marker, downloads_like, seen_like, current_seen_marker),
            )
            conn.commit()

    def _upsert_by_inode(self, conn: sqlite3.Connection, row: dict[str, object], marker: str) -> bool:
        dev = row["dev"]
        inode = row["inode"]
        if dev is None or inode is None:
            return False

        cursor = conn.execute(
            "SELECT id FROM episode_file_cache WHERE dev = ? AND inode = ? LIMIT 1",
            (dev, inode),
        )
        hit = cursor.fetchone()
        if not hit:
            return False

        conn.execute(
            """
            UPDATE episode_file_cache
            SET path = ?, folder_state = ?, size_bytes = ?, mtime_ns = ?, dev = ?, inode = ?,
                fingerprint = ?, last_seen_at = ?
            WHERE id = ?
            """,
            (
                row["path"],
                row["folder_state"],
                row["size_bytes"],
                row["mtime_ns"],
                row["dev"],
                row["inode"],
                row["fingerprint"],
                marker,
                hit[0],
            ),
        )
        return True

    def _upsert_by_fingerprint(self, conn: sqlite3.Connection, row: dict[str, object], marker: str) -> bool:
        cursor = conn.execute(
            """
            SELECT id FROM episode_file_cache
            WHERE fingerprint = ? AND size_bytes = ?
            ORDER BY id ASC
            LIMIT 1
            """,
            (row["fingerprint"], row["size_bytes"]),
        )
        hit = cursor.fetchone()
        if not hit:
            return False

        conn.execute(
            """
            UPDATE episode_file_cache
            SET path = ?, folder_state = ?, size_bytes = ?, mtime_ns = ?, dev = ?, inode = ?,
                fingerprint = ?, last_seen_at = ?
            WHERE id = ?
            """,
            (
                row["path"],
                row["folder_state"],
                row["size_bytes"],
                row["mtime_ns"],
                row["dev"],
                row["inode"],
                row["fingerprint"],
                marker,
                hit[0],
            ),
        )
        return True

    def _scan(self, folder: str, folder_state: str, extension: str) -> list[dict[str, object]]:
        root: Path = Path(folder).resolve()
        if not root.exists():
            return []

        rows: list[dict[str, object]] = []
        for entry in root.iterdir():
            if not entry.is_file() or entry.suffix.lower() != extension.lower():
                continue
            stat = entry.stat()
            rows.append(
                {
                    "path": str(entry),
                    "folder_state": folder_state,
                    "size_bytes": int(stat.st_size),
                    "mtime_ns": int(stat.st_mtime_ns),
                    "dev": int(getattr(stat, "st_dev", 0)),
                    "inode": int(getattr(stat, "st_ino", 0)),
                    "fingerprint": self._fingerprint(entry, int(stat.st_size)),
                }
            )
        return rows

    def _fingerprint(self, path: Path, size: int) -> str:
        hasher = hashlib.sha1()
        hasher.update(str(size).encode("utf-8"))
        with path.open("rb") as handle:
            head = handle.read(65536)
            hasher.update(head)
            if size > 65536:
                handle.seek(max(0, size - 65536))
                tail = handle.read(65536)
                hasher.update(tail)
        return hasher.hexdigest()
