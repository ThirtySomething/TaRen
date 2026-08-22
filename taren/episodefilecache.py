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
from pathlib import Path

from taren.filefingerprint import FileFingerprint
from taren.helper import Helper

logger = logging.getLogger(__name__)


class EpisodeFileCache:
    """In-memory index of episode files discovered on disk.

    This implementation maintains an in-memory fingerprint index keyed by
    (fingerprint, size_bytes) and does not persist any data to disk. The index
    is rebuilt from the seen/unseen folders during reconcile().
    """

    def __init__(self, db_path: str) -> None:
        self._db_path: str = db_path
        # In-memory index mapping (fingerprint, size_bytes) -> absolute path
        self._fingerprint_index: dict[tuple[str, int], str] = {}

    def initialize(self) -> None:
        """Prepare the in-memory index. No on-disk persistence is used."""
        self._fingerprint_index = {}

    def reconcile(self, downloads_dir: str, seen_dir: str, unseen_dir: str, extension: str) -> None:
        """Rebuild the in-memory index from the seen and unseen folders.

        Downloads are not persisted in this in-memory-only implementation; the
        index reflects the current filesystem state of seen/unseen folders.
        """
        normalized_ext: str = Helper.normalize_extension(extension)
        try:
            self._rebuild_in_memory_index(seen_dir, unseen_dir, normalized_ext)
        except Exception:
            logger.debug("in_memory_index_rebuild_failed", exc_info=True)

    def find_existing_by_fingerprint(self, fingerprint: str, size_bytes: int) -> str | None:
        """
        Find an existing file copy in seen or unseen folders by fingerprint using
        the in-memory index populated by reconcile.

        Returns path if found, otherwise None.
        """
        key = (fingerprint, int(size_bytes))
        return self._fingerprint_index.get(key)


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

    def _rebuild_in_memory_index(self, seen_dir: str, unseen_dir: str, extension: str) -> None:
        """
        Rebuild the in-memory fingerprint index from the current contents of the
        seen and unseen folders. Called at the end of reconcile to make
        find_existing_by_fingerprint fast and DB-free.
        """
        new_index: dict[tuple[str, int], str] = {}
        seen_rows = self._scan(seen_dir, "seen", extension)
        unseen_rows = self._scan(unseen_dir, "unseen", extension)
        for row in seen_rows + unseen_rows:
            # Prefer seen over unseen if a fingerprint is present multiple times.
            key = (row["fingerprint"], int(row["size_bytes"]))
            # If a seen entry already exists, keep it; otherwise set from unseen.
            if key in new_index and row["folder_state"] == "unseen":
                continue
            new_index[key] = str(Path(row["path"]).resolve())
        self._fingerprint_index = new_index

    def _fingerprint(self, path: Path, size: int) -> str:
        # Keep method signature for compatibility with existing tests/callers.
        _ = size
        return FileFingerprint.compute(path)
