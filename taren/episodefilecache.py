"""
******************************************************************************
Copyright 2020 ThirtySomething
******************************************************************************
This file is part of TaRen.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
******************************************************************************
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from taren.filefingerprint import FileFingerprint
from taren.helper import Helper

logger = logging.getLogger(__name__)


class EpisodeFileCache:
    """SQLite-backed index of episode files discovered on disk."""

    def __init__(self, db_path: str) -> None:
        self._db_path: str = db_path

    def initialize(self) -> None:
        conn = sqlite3.connect(self._db_path)
        try:
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
        finally:
            conn.close()

    def reconcile(self, downloads_dir: str, seen_dir: str, unseen_dir: str, extension: str) -> None:
        self.initialize()
        normalized_ext: str = Helper.normalize_extension(extension)
        observed = self._scan(downloads_dir, "downloads", normalized_ext)
        observed.extend(self._scan(seen_dir, "seen", normalized_ext))
        observed.extend(self._scan(unseen_dir, "unseen", normalized_ext))

        current_seen_marker: str = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        conn = sqlite3.connect(self._db_path)
        try:
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
            unseen_like = f"{Path(unseen_dir).resolve()}{os.sep}%"
            conn.execute(
                """
                UPDATE episode_file_cache
                SET folder_state = 'missing', last_seen_at = ?
                WHERE (path LIKE ? OR path LIKE ? OR path LIKE ?)
                  AND last_seen_at <> ?
                """,
                (current_seen_marker, downloads_like, seen_like, unseen_like, current_seen_marker),
            )
            conn.commit()
        finally:
            conn.close()

    def find_existing_by_fingerprint(self, fingerprint: str, size_bytes: int) -> str | None:
        """
        Find an existing file copy in seen or unseen folders by fingerprint.

        This enables fast duplicate detection: if a download file matches a file
        already in seen or unseen (same size and fingerprint), we can skip it.

        Args:
            fingerprint: SHA-1 fingerprint (size + head + tail)
            size_bytes: File size in bytes

        Returns:
            Path to existing file if found in seen or unseen, None otherwise
        """
        try:
            conn = sqlite3.connect(self._db_path)
            try:
                cursor = conn.execute(
                    """
                    SELECT path FROM episode_file_cache
                    WHERE fingerprint = ? AND size_bytes = ?
                      AND folder_state IN ('seen', 'unseen')
                    LIMIT 1
                    """,
                    (fingerprint, size_bytes),
                )
                result = cursor.fetchone()
                return result[0] if result else None
            finally:
                conn.close()
        except sqlite3.DatabaseError as exc:
            logger.warning(
                "cache_lookup_failed: fingerprint=%s size=%s error=%s",
                fingerprint,
                size_bytes,
                exc,
            )
            return None

    def _update_row(self, conn: sqlite3.Connection, row_id: int, row: dict[str, object], marker: str) -> None:
        """
        Update an existing cache row with new file metadata.

        Args:
            conn: Database connection
            row_id: ID of row to update
            row: File metadata dict containing path, folder_state, size_bytes, mtime_ns, dev, inode, fingerprint
            marker: Current seen marker timestamp
        """
        # Ensure we won't violate the UNIQUE constraint on `path` when
        # updating this row to a new path that might already exist in
        # another row. Remove any other rows that have the same path but
        # a different id to merge/replace them.
        conn.execute(
            "DELETE FROM episode_file_cache WHERE path = ? AND id <> ?",
            (row["path"], row_id),
        )

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
                row_id,
            ),
        )

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

        self._update_row(conn, hit[0], row, marker)
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

        self._update_row(conn, hit[0], row, marker)
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
        # Keep method signature for compatibility with existing tests/callers.
        _ = size
        return FileFingerprint.compute(path)
