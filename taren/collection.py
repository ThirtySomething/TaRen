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
        self._ignorefile: str = trash_ignore
        self._downloads: Path = self._root / TarenDefines.FOLDER_DOWNLOADS
        self._seen: Path = self._root / TarenDefines.FOLDER_SEEN
        self._unseen: Path = self._root / TarenDefines.FOLDER_UNSEEN
        self._trash: Path = self._root / TarenDefines.FOLDER_TRASH
        self._seen_ignore_path: Path = self._seen / self._ignorefile
        self._trash_ignore_path: Path = self._trash / self._ignorefile
        logger.debug(
            "collection_init: root=%s downloads=%s seen=%s unseen=%s trash=%s trash_ignore=%s",
            self._root,
            self._downloads,
            self._seen,
            self._unseen,
            self._trash,
            self._ignorefile,
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

        # Ensure ignore marker exists in trash folder so media indexers can skip it.
        if not self._trash_ignore_path.exists():
            self._trash_ignore_path.touch()
            logger.debug("collection_trash_ignore_ready: path=%s", self._trash_ignore_path)

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
    def get_reconcile_paths(self) -> tuple[str, str, str]:
        """
        Get source folder paths used for cache reconciliation.

        Returns:
            Tuple of (downloads_path, seen_path, unseen_path) as strings
        """
        return str(self._downloads), str(self._seen), str(self._unseen)

    ############################################################################
    def collect_download_matching_files(self, pattern: str, extension: str) -> tuple[int, list[tuple[str, str]]]:
        """
        Collect matching filenames from the downloads folder only.

        Args:
            pattern: Filename pattern to match
            extension: File extension filter

        Returns:
            Tuple of (total files in downloads, list of (source_dir, filename))
        """
        if not self._downloads.exists():
            logger.warning("downloads_folder_missing: path=%s", self._downloads)
            return 0, []

        filelist: list[str] = DownloadList(str(self._downloads), pattern, extension).get_filenames()
        return len(filelist), [(str(self._downloads), filename) for filename in filelist]

    ############################################################################
    def resolve_episode_paths(self, episode_name: str, extension: str) -> tuple[Path, Path]:
        """
        Resolve conflict-check and final destination paths for one episode.

        Resolution order:
        - If episode exists in seen, compare against seen and keep destination in seen.
        - Else if episode exists in unseen, compare against unseen and move replacement to seen.
        - Else place new download into unseen.

        Args:
            episode_name: Canonical episode filename without extension
            extension: File extension to append

        Returns:
            Tuple of (conflict_check_path, destination_path)
        """
        normalized_extension: str = Helper.normalize_extension(extension)
        seen_target: Path = self._seen / f"{episode_name}{normalized_extension}"
        unseen_target: Path = self._unseen / f"{episode_name}{normalized_extension}"

        if seen_target.exists():
            return seen_target, seen_target
        if unseen_target.exists():
            return unseen_target, seen_target
        return unseen_target, unseen_target

    ############################################################################
    def _list_folder(self, folder: Path, label: str, excluded: set[str] | None = None) -> list[str]:
        """
        Helper to list files in a folder, excluding specified names.

        Args:
            folder: Folder path to list
            label: Label for warning messages (e.g., "downloads", "seen")
            excluded: Set of filenames to exclude (ignore markers)

        Returns:
            Sorted list of filenames, excluding ignore markers
        """
        if not folder.exists():
            logger.warning("%s_folder_missing: path=%s", label, folder)
            return []
        excluded = excluded or set()
        return sorted(f.name for f in folder.iterdir() if f.is_file() and f.name not in excluded)

    ############################################################################
    def get_downloads(self) -> list[str]:
        """
        Get list of files in the downloads folder.

        Returns:
            List of filenames in downloads folder, sorted alphabetically
        """
        return self._list_folder(self._downloads, "downloads")

    ############################################################################
    def get_seen(self) -> list[str]:
        """
        Get list of files in the seen folder.

        Returns:
            List of filenames in seen folder (excluding ignore marker), sorted alphabetically
        """
        excluded = {self._ignorefile}
        return self._list_folder(self._seen, "seen", excluded)

    ############################################################################
    def get_trash(self) -> list[str]:
        """
        Get list of files in the trash folder.

        Returns:
            List of filenames in trash folder (excluding ignore marker), sorted alphabetically
        """
        excluded = {self._ignorefile}
        return self._list_folder(self._trash, "trash", excluded)

    ############################################################################
    def get_unseen(self) -> list[str]:
        """
        Get list of files in the unseen folder.

        Returns:
            List of unseen filenames, sorted alphabetically
        """
        return self._list_folder(self._unseen, "unseen")

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
    def get_counts(self) -> dict[str, int]:
        """
        Get counts of items in all collection categories.

        Returns:
            Dictionary with counts: {downloads, seen, unseen, trash}
        """
        return self.get_stats()["counts"]

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
