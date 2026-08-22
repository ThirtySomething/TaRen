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

from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import os
from pathlib import Path

from taren.collection import Collection
from taren.conflictresolutionresult import ConflictResolutionResult
from taren.conflictresolutionstrategy import ConflictResolutionStrategy
from taren.downloadtask import DownloadTask
from taren.episode import Episode
from taren.episodefilecache import EpisodeFileCache
from taren.episodelist import EpisodeList
from taren.filesystemerror import FileSystemError
from taren.filefingerprint import FileFingerprint
from taren.filemutationcommand import FileMutationCommand
from taren.movetotrashcommand import MoveToTrashCommand
from taren.renamefilecommand import RenameFileCommand
from taren.helper import Helper
from taren.requestshttpfetchpolicy import RequestsHttpFetchPolicy
from taren.sizebasedconflictstrategy import SizeBasedConflictStrategy
from taren.stats import Stats
from taren.tarendefines import TarenDefines
from taren.tarenconfig import TarenConfig
from taren.trash import Trash

logger = logging.getLogger(__name__)


class TaRen:
    """
    Controlls the process of 'TAtort RENaming':
    - Download, parsing and list of Wiki page about episodes
    - Search for downloaded episodes
    - Perform renaming
    """

    def __init__(
        self,
        config: TarenConfig,
        conflict_strategy: ConflictResolutionStrategy | None = None,
    ) -> None:
        self._config: TarenConfig = config
        collection_root: Path = Path(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_COLLECTION))
        trash_ignore: str = self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_TRASHIGNORE)
        self._collection_manager: Collection = Collection(collection_root, trash_ignore=trash_ignore)
        self._collection: Path = collection_root
        self._pattern: str = self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_PATTERN)
        self._extension: str = Helper.normalize_extension(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_EXTENSION))
        self._url: str = self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_WIKI)
        self._cachetime: int = int(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_MAXCACHE))
        self._trashage: int = int(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_TRASHAGE))
        self._http_timeout: float = float(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_HTTP_TIMEOUT))
        self._http_retries: int = int(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_HTTP_RETRIES))
        # EpisodeFileCache is in-memory now; pass an empty string for compatibility
        self._episode_file_cache: EpisodeFileCache = EpisodeFileCache("")
        self._max_parallel_workers: int = self._determine_parallel_workers()
        self._conflict_strategy: ConflictResolutionStrategy = conflict_strategy or SizeBasedConflictStrategy()
        self._trash: Trash = Trash(
            str(self._collection),
            TarenDefines.FOLDER_TRASH,
            self._trashage,
            trash_ignore,
        )
        self._log_initialization()

    ############################################################################
    def _log_initialization(self) -> None:
        """Log configuration details during initialization."""
        logger.debug(
            "taren_init: collection=%s downloads=%s seen=%s status=ready",
            self._collection_manager.get_root_path(),
            self._collection_manager.get_downloads_path(),
            self._collection_manager.get_seen_path(),
        )
        logger.debug(
            "taren_init: pattern=%s extension=%s url=%s status=ready",
            self._pattern,
            self._extension,
            self._url,
        )
        logger.debug(
            "taren_init: maxcache_days=%s http_timeout=%s http_retries=%s status=ready",
            self._cachetime,
            self._http_timeout,
            self._http_retries,
        )
        logger.debug(
            "taren_init: parallel_workers=%s status=ready",
            self._max_parallel_workers,
        )
        logger.debug(
            "taren_init: trash_age_days=%s trash_strategy=%s conflict_strategy=%s status=ready",
            self._trashage,
            type(self._trash).__name__,
            type(self._conflict_strategy).__name__,
        )

    ############################################################################
    def _calculate_parallel_workers(self) -> int:
        """Determine conservative automatic worker count for file task parallelism."""
        cpu_count: int = os.cpu_count() or 1
        return max(1, min(4, cpu_count))

    ############################################################################
    def _determine_parallel_workers(self) -> int:
        """Resolve worker count from config and clamp to a safe runtime range."""
        auto_workers: int = self._calculate_parallel_workers()
        try:
            configured_workers: int = int(
                self._config.value_get(
                    TarenDefines.CFG_SECTION_TAREN,
                    TarenDefines.CFG_KEY_PARALLEL_WORKERS,
                )
            )
        except (KeyError, ValueError, TypeError):
            logger.debug(
                "parallel_workers_config: status=fallback reason=missing_or_invalid auto_workers=%s",
                auto_workers,
            )
            return auto_workers

        cpu_count: int = os.cpu_count() or 1
        return max(1, min(configured_workers, cpu_count, 32))

    ############################################################################
    def _compute_fingerprint(self, file_path: Path) -> str:
        """
        Compute file fingerprint for cache lookups.
        """
        return FileFingerprint.compute(file_path)

    ############################################################################
    def rename_process(self) -> None:
        """
        Controls the complete process:
        - Get website content about the episodes
        - Build internal list about episodes
        - Find affected downloads
        """

        if not self._preflight():
            return

        statistics: Stats = Stats()
        episode_list: EpisodeList = self._load_episodes(statistics)
        downloads_to_process: list[DownloadTask] | None = self._collect_tasks(episode_list, statistics)
        if downloads_to_process is None:
            return
        self._process_tasks(downloads_to_process, statistics)
        self._finalize(statistics)

    ############################################################################
    def _preflight(self) -> bool:
        """Perform required pre-checks before processing."""

        # Check collection root exists
        if not self._collection.exists():
            logger.error(
                "preflight_collection: path=%s status=missing",
                self._collection,
            )
            return False

        # Initialize collection folder structure
        if not self._collection_manager.initialize():
            logger.error(
                "preflight_collection_init: path=%s status=failed",
                self._collection,
            )
            return False

        try:
            self._episode_file_cache.initialize()
        except OSError as exc:
            logger.error("episode_cache_init: status=failed error=%s", exc)
            return False

        return True

    ############################################################################
    def _load_episodes(self, statistics: Stats) -> EpisodeList:
        """Load episode metadata from configured source."""

        # Get list of episodes from web page
        ua: str = self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_WIKI_USERAGENT)
        fetch_policy = RequestsHttpFetchPolicy(timeout_seconds=self._http_timeout, retries=self._http_retries)
        episode_list: EpisodeList = EpisodeList(
            self._pattern,
            self._url,
            self._cachetime,
            ua,
            fetch_policy=fetch_policy,
            cache_dir=str(self._collection),
        )
        episode_list.get_episodes()
        statistics.episodes_total = episode_list.get_episode_count()
        return episode_list

    ############################################################################
    def _initialize_trash(self) -> bool:
        """Initialize trash folder and marker file."""

        try:
            self._trash.init()
            return True
        except FileSystemError as exc:
            logger.error("trash_init: status=failed error=%s", exc)
            return False

    ############################################################################
    def _reconcile_episode_cache(self) -> None:
        """Reconcile episode file cache with current collection state."""

        downloads_path: Path = self._collection_manager.get_downloads_path()
        seen_path: Path = self._collection_manager.get_seen_path()
        unseen_path: Path = self._collection_manager.get_unseen_path()
        try:
            self._episode_file_cache.reconcile(str(downloads_path), str(seen_path), str(unseen_path), self._extension)
        except OSError as exc:
            logger.error("episode_cache_reconcile: status=failed error=%s", exc)

    ############################################################################
    def _should_skip_duplicate(self, download_path: Path, filename: str) -> bool:
        """Return True when a download is already present in cache by fingerprint."""

        if not download_path.exists():
            return False

        try:
            fingerprint = self._compute_fingerprint(download_path)
            existing = self._episode_file_cache.find_existing_by_fingerprint(fingerprint, download_path.stat().st_size)
            if existing:
                logger.info(
                    "task_skip_duplicate: filename=%s reason=exists_in_cache existing_path=%s",
                    filename,
                    existing,
                )
                return True
        except OSError as exc:
            logger.warning(
                "task_fingerprint_failed: filename=%s error=%s status=fallback",
                filename,
                exc,
            )

        return False

    ############################################################################
    def _build_download_tasks(self, episode_list: EpisodeList) -> tuple[int, list[DownloadTask]]:
        """Build processable download tasks with known episode metadata."""

        downloads_to_process: list[DownloadTask] = []
        total_files, matches = self._collection_manager.collect_download_matching_files(self._pattern, self._extension)
        for sourcedir, current_download in matches:
            download_path = Path(sourcedir) / current_download

            episode: Episode = episode_list.find_episode(current_download)
            if episode.empty:
                continue

            downloads_to_process.append(DownloadTask(filename=current_download, episode=episode, sourcedir=sourcedir))

        return total_files, downloads_to_process

    ############################################################################
    def _collect_tasks(self, episode_list: EpisodeList, statistics: Stats) -> list[DownloadTask] | None:
        """Collect downloads that can be processed with known episode metadata."""

        if not self._initialize_trash():
            return None

        self._reconcile_episode_cache()
        total_files, downloads_to_process = self._build_download_tasks(episode_list)
        logger.info(
            "task_collection: total_files=%s candidates=%s status=ready",
            total_files,
            len(downloads_to_process),
        )
        return downloads_to_process

    ############################################################################
    def _process_tasks(self, downloads_to_process: list[DownloadTask], statistics: Stats) -> None:
        """Apply rename and conflict handling for prepared tasks."""

        if len(downloads_to_process) <= 1 or self._max_parallel_workers == 1:
            for current_download in downloads_to_process:
                self._process_single_task(current_download)
            return

        logger.info(
            "task_processing: mode=parallel workers=%s tasks=%s status=started",
            self._max_parallel_workers,
            len(downloads_to_process),
        )
        with ThreadPoolExecutor(max_workers=self._max_parallel_workers) as executor:
            futures = {executor.submit(self._process_single_task, task): task for task in downloads_to_process}
            for future in as_completed(futures):
                try:
                    future.result()
                except (OSError, IOError, FileNotFoundError) as exc:
                    task = futures[future]
                    logger.error("task_failed: file=%s error=%s", task.filename, exc)
                except Exception as exc:
                    task = futures[future]
                    logger.exception("task_unexpected_error: file=%s error=%s", task.filename, exc)
                    raise

    ############################################################################
    def _process_single_task(self, current_download: DownloadTask) -> None:
        """Process one download task."""

        old_path: Path = Path(current_download.sourcedir) / current_download.filename
        conflict_check_path, destination_path = self._collection_manager.resolve_episode_paths(
            str(current_download.episode),
            self._extension,
        )

        if old_path == conflict_check_path or old_path == destination_path:
            return

        conflict_result: ConflictResolutionResult = self._conflict_strategy.resolve(str(old_path), str(conflict_check_path))
        commands: list[FileMutationCommand] = self._build_commands_for_task(old_path, destination_path, conflict_result)
        if not self._execute_commands(commands):
            logger.warning("task_processing_incomplete: file=%s", current_download.filename)

    ############################################################################
    def _build_commands_for_task(
        self,
        old_path: Path | str,
        new_path: Path | str,
        conflict_result: ConflictResolutionResult,
    ) -> list[FileMutationCommand]:
        """Factory method for building mutation commands for one task."""

        old_path = Path(old_path)
        new_path = Path(new_path)
        commands: list[FileMutationCommand] = []
        if conflict_result.move_to_trash is not None:
            trash_path: Path = Path(conflict_result.move_to_trash)
            if trash_path == old_path:
                # Download is going to trash: normalize its filename first so trash
                # contains identifiable names.  Keep the original file extension.
                normalized_name = new_path.stem + old_path.suffix
                normalized_path: Path = old_path.parent / normalized_name
                if normalized_path != old_path:
                    commands.append(RenameFileCommand(str(old_path), str(normalized_path)))
                trash_path = normalized_path
            commands.append(MoveToTrashCommand(self._trash, str(trash_path)))
        if not conflict_result.skip_rename:
            commands.append(RenameFileCommand(str(old_path), str(new_path)))
        return commands

    ############################################################################
    def _execute_commands(self, commands: list[FileMutationCommand]) -> bool:
        """Execute prepared file-mutation commands in order.

        Returns True if all commands succeeded, else False.
        """

        for command in commands:
            if not command.execute():
                logger.error("task_execution: status=aborted reason=previous_failure")
                return False
        return True

    ############################################################################
    def _finalize(self, statistics: Stats) -> None:
        """Finalize processing by handling trash maintenance and summary logging."""

        # Maintain trash folder before counting collection state.
        self._trash.cleanup()
        self._trash.list()

        # Populate collection statistics
        collection_counts = self._collection_manager.get_counts()
        statistics.collection_downloads = collection_counts["downloads"]
        statistics.collection_seen = collection_counts["seen"]
        statistics.collection_unseen = collection_counts["unseen"]
        statistics.collection_trash = collection_counts["trash"]

        # Update episodes_owned to reflect collection content
        statistics.update_episodes_owned_from_collection()

        # Log collection summary
        self._collection_manager.log_summary()

        # Summary
        logger.info("run_summary: status=completed details=%s", statistics)

    ############################################################################
    def get_collection_manager(self) -> Collection:
        """
        Get the collection manager to query collection contents.

        Returns:
            Collection manager instance for accessing downloads, seen, trash, and unseen items
        """
        return self._collection_manager
