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
from typing import Any

from taren.downloadlist import DownloadList
from taren.helper import Helper
from taren.tarendefines import TarenDefines

logger = logging.getLogger(__name__)


class Collection:
    """
    Manages the collection folder structure with organized subfolders:
    - downloads: Files to be processed
    - seen: Already processed files
    - unseen: Files awaiting processing
    - trash: Deleted files
    """

    ############################################################################
    def __init__(self, root_path: Path, trash_ignore: str = ".ignore") -> None:
        """
        Initialize collection with root path and organize subfolders.

        Args:
            root_path: Root path of the collection from config
            trash_ignore: Marker filename to exclude from trash counters
        """
        self._root: Path = root_path
        self._trash_ignore: str = trash_ignore
        self._downloads: Path = self._root / TarenDefines.FOLDER_DOWNLOADS
        self._seen: Path = self._root / TarenDefines.FOLDER_SEEN
        self._unseen: Path = self._root / TarenDefines.FOLDER_UNSEEN
        self._trash: Path = self._root / TarenDefines.FOLDER_TRASH
        self._seen_ignore_path: Path = self._seen / self._trash_ignore
        logger.debug(
            "collection_init: root=%s downloads=%s seen=%s unseen=%s trash=%s trash_ignore=%s",
            self._root,
            self._downloads,
            self._seen,
            self._unseen,
            self._trash,
            self._trash_ignore,
        )

    ############################################################################
    def initialize(self) -> bool:
        """
        Ensure all collection subfolders exist.

        Returns:
            True if all folders initialized successfully, False otherwise
        """
        folders = [
            (self._downloads, "downloads"),
            (self._seen, "seen"),
            (self._unseen, "unseen"),
            (self._trash, "trash"),
        ]

        for folder_path, folder_name in folders:
            if not Helper.ensure_directory(str(folder_path)):
                logger.error(
                    "collection_init_failed: folder=%s path=%s",
                    folder_name,
                    folder_path,
                )
                return False
            logger.debug("collection_folder_ready: folder=%s path=%s", folder_name, folder_path)

        # Ensure ignore marker exists in seen folder so media indexers can skip it.
        if not self._seen_ignore_path.exists():
            self._seen_ignore_path.touch()
            logger.debug("collection_seen_ignore_ready: path=%s", self._seen_ignore_path)

        return True

    ############################################################################
    def get_root_path(self) -> Path:
        """
        Get the root collection path.

        Returns:
            Root collection path
        """
        return self._root

    ############################################################################
    def get_downloads_path(self) -> Path:
        """
        Get the downloads folder path.

        Returns:
            Downloads folder path
        """
        return self._downloads

    ############################################################################
    def get_seen_path(self) -> Path:
        """
        Get the seen folder path.

        Returns:
            Seen folder path
        """
        return self._seen

    ############################################################################
    def get_unseen_path(self) -> Path:
        """
        Get the unseen folder path.

        Returns:
            Unseen folder path
        """
        return self._unseen

    ############################################################################
    def get_trash_path(self) -> Path:
        """
        Get the trash folder path.

        Returns:
            Trash folder path
        """
        return self._trash

    ############################################################################
    def get_processing_sources(self) -> tuple[Path, Path, Path]:
        """
        Get source folders that are scanned for matching episode files.

        Returns:
            Tuple of (downloads_path, seen_path, unseen_path)
        """
        return self._downloads, self._seen, self._unseen

    ############################################################################
    def get_reconcile_paths(self) -> tuple[str, str, str]:
        """
        Get source folder paths used for cache reconciliation.

        Returns:
            Tuple of (downloads_path, seen_path, unseen_path) as strings
        """
        downloads_path, seen_path, unseen_path = self.get_processing_sources()
        return str(downloads_path), str(seen_path), str(unseen_path)

    ############################################################################
    def collect_matching_files(self, pattern: str, extension: str) -> tuple[int, list[tuple[str, str]]]:
        """
        Collect matching filenames from collection processing sources.

        Args:
            pattern: Filename pattern to match
            extension: File extension filter

        Returns:
            Tuple of (total files in scanned sources, list of (source_dir, filename))
        """
        total_files: int = 0
        matches: list[tuple[str, str]] = []

        for sourcedir in self.get_processing_sources():
            if not sourcedir.exists():
                logger.debug("collection_scan_skipped: path=%s status=missing", sourcedir)
                continue
            filelist: list[str] = DownloadList(str(sourcedir), pattern, extension).get_filenames()
            total_files += len(filelist)
            for filename in filelist:
                matches.append((str(sourcedir), filename))

        return total_files, matches

    ############################################################################
    def get_downloads(self) -> list[str]:
        """
        Get list of files in the downloads folder.

        Returns:
            List of filenames in downloads folder, sorted alphabetically
        """
        if not self._downloads.exists():
            logger.warning("downloads_folder_missing: path=%s", self._downloads)
            return []

        files = [f.name for f in self._downloads.iterdir() if f.is_file()]
        return sorted(files)

    ############################################################################
    def get_seen(self) -> list[str]:
        """
        Get list of files in the seen folder.

        Returns:
            List of filenames in seen folder (excluding ignore marker), sorted alphabetically
        """
        if not self._seen.exists():
            logger.warning("seen_folder_missing: path=%s", self._seen)
            return []

        excluded_names: set[str] = {self._trash_ignore, ".seenignore"}
        files = [f.name for f in self._seen.iterdir() if f.is_file() and f.name not in excluded_names]
        return sorted(files)

    ############################################################################
    def get_trash(self) -> list[str]:
        """
        Get list of files in the trash folder.

        Returns:
            List of filenames in trash folder (excluding ignore marker), sorted alphabetically
        """
        if not self._trash.exists():
            logger.warning("trash_folder_missing: path=%s", self._trash)
            return []

        files = []
        excluded_names: set[str] = {self._trash_ignore, ".trashignore"}
        for f in self._trash.iterdir():
            if f.is_file() and f.name not in excluded_names:
                files.append(f.name)
        return sorted(files)

    ############################################################################
    def get_unseen(self) -> list[str]:
        """
        Get list of files in the unseen folder.

        Returns:
            List of unseen filenames, sorted alphabetically
        """
        if not self._unseen.exists():
            logger.warning("unseen_folder_missing: path=%s", self._unseen)
            return []

        files = [f.name for f in self._unseen.iterdir() if f.is_file()]
        return sorted(files)

    ############################################################################
    def get_counts(self) -> dict[str, int]:
        """
        Get counts of items in all collection categories.

        Returns:
            Dictionary with counts: {downloads, seen, unseen, trash}
        """
        downloads = self.get_downloads()
        seen = self.get_seen()
        unseen = self.get_unseen()
        trash = self.get_trash()

        return {
            "downloads": len(downloads),
            "seen": len(seen),
            "unseen": len(unseen),
            "trash": len(trash),
        }

    ############################################################################
    def get_stats(self) -> dict[str, Any]:
        """
        Get detailed statistics of the collection.

        Returns:
            Dictionary with counts and lists for all categories
        """
        downloads = self.get_downloads()
        seen = self.get_seen()
        unseen = self.get_unseen()
        trash = self.get_trash()

        return {
            "counts": {
                "downloads": len(downloads),
                "seen": len(seen),
                "unseen": len(unseen),
                "trash": len(trash),
            },
            "items": {
                "downloads": downloads,
                "seen": seen,
                "unseen": unseen,
                "trash": trash,
            },
        }

    ############################################################################
    def log_summary(self) -> None:
        """Log a summary of collection contents."""
        counts = self.get_counts()
        logger.info(
            "collection_summary: downloads=%d seen=%d unseen=%d trash=%d",
            counts["downloads"],
            counts["seen"],
            counts["unseen"],
            counts["trash"],
        )
