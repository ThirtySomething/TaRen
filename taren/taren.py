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

from concurrent.futures import ThreadPoolExecutor
import logging
import os
from pathlib import Path

from taren.conflictresolutionresult import ConflictResolutionResult
from taren.conflictresolutionstrategy import ConflictResolutionStrategy
from taren.downloadlist import DownloadList
from taren.downloadtask import DownloadTask
from taren.episode import Episode
from taren.episodelist import EpisodeList
from taren.filemutationcommand import FileMutationCommand
from taren.movetotrashcommand import MoveToTrashCommand
from taren.renamefilecommand import RenameFileCommand
from taren.helper import Helper
from taren.requestshttpfetchpolicy import RequestsHttpFetchPolicy
from taren.sizebasedconflictstrategy import SizeBasedConflictStrategy
from taren.stats import Stats
from taren.tarendefines import FileSystemError, TarenDefines
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
        self._collection: Path = self._sanitize_path(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_COLLECTION))
        self._downloads: Path = self._collection / TarenDefines.FOLDER_DOWNLOADS
        self._seen: Path = self._collection / TarenDefines.FOLDER_SEEN
        self._pattern: str = self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_PATTERN)
        self._extension: str = self._sanitize_extension(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_EXTENSION))
        self._url: str = self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_WIKI)
        self._cachetime: int = int(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_MAXCACHE))
        self._trashage: int = int(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_TRASHAGE))
        self._http_timeout: float = float(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_HTTP_TIMEOUT))
        self._http_retries: int = int(self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_HTTP_RETRIES))
        self._max_parallel_workers: int = self._determine_parallel_workers()
        self._conflict_strategy: ConflictResolutionStrategy = conflict_strategy or SizeBasedConflictStrategy()
        self._trash: Trash = Trash(
            str(self._collection),
            TarenDefines.FOLDER_TRASH,
            self._trashage,
            self._config.value_get(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_TRASHIGNORE),
        )
        self._log_initialization()

    ############################################################################
    def _log_initialization(self) -> None:
        """Log configuration details during initialization."""
        logger.debug(
            "taren_init: collection=%s downloads=%s seen=%s status=ready",
            self._collection,
            self._downloads,
            self._seen,
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
    def _sanitize_extension(self, extension: str) -> str:
        """
        Ensure extension starts with a dot
        """
        if not extension.startswith("."):
            extension = f".{extension}"
        return extension

    ############################################################################
    def _sanitize_path(self, path: str) -> Path:
        """
        Normalize configured path into a pathlib.Path instance
        """
        return Path(path)

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

        # Ensure downloads and seen subfolders exist
        if not Helper.ensure_directory(self._downloads):
            logger.error(
                "preflight_directory: path=%s kind=downloads status=failed",
                self._downloads,
            )
            return False

        if not Helper.ensure_directory(self._seen):
            logger.error(
                "preflight_directory: path=%s kind=seen status=failed",
                self._seen,
            )
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
    def _collect_tasks(self, episode_list: EpisodeList, statistics: Stats) -> list[DownloadTask] | None:
        """Collect downloads that can be processed with known episode metadata."""

        # Check for trash
        try:
            self._trash.init()
        except FileSystemError as e:
            logger.error("trash_init: status=failed error=%s", e)
            return None

        # Scan both downloads/ and seen/ for matching files
        downloads_to_process: list[DownloadTask] = []
        total_files: int = 0
        for sourcedir in (self._downloads, self._seen):
            filelist: list[str] = DownloadList(str(sourcedir), self._pattern, self._extension).get_filenames()
            total_files += len(filelist)
            for current_download in filelist:
                episode: Episode = episode_list.find_episode(current_download)
                if episode.empty:
                    continue
                downloads_to_process.append(DownloadTask(filename=current_download, episode=episode, sourcedir=str(sourcedir)))
        statistics.downloads_total = total_files
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
                task_stats: Stats = self._process_single_task(current_download)
                self._merge_task_stats(statistics, task_stats)
            return

        logger.info(
            "task_processing: mode=parallel workers=%s tasks=%s status=started",
            self._max_parallel_workers,
            len(downloads_to_process),
        )
        with ThreadPoolExecutor(max_workers=self._max_parallel_workers) as executor:
            for task_stats in executor.map(self._process_single_task, downloads_to_process):
                self._merge_task_stats(statistics, task_stats)

    ############################################################################
    def _process_single_task(self, current_download: DownloadTask) -> Stats:
        """Process one download task and return local task statistics."""

        task_stats: Stats = Stats()

        new_fqn_path: Path = self._seen / f"{current_download.episode}{self._extension}"
        old_fqn_path: Path = Path(current_download.sourcedir) / current_download.filename

        if new_fqn_path == old_fqn_path:
            # Already processed episode
            task_stats.episodes_owned += 1
            return task_stats

        new_fqn: str = str(new_fqn_path)
        old_fqn: str = str(old_fqn_path)
        conflict_result: ConflictResolutionResult = self._conflict_strategy.resolve(old_fqn, new_fqn)
        commands: list[FileMutationCommand] = self._build_commands_for_task(old_fqn, new_fqn, conflict_result)
        self._execute_commands(commands, task_stats)
        return task_stats

    ############################################################################
    def _merge_task_stats(self, statistics: Stats, task_stats: Stats) -> None:
        """Merge local per-task stats into global run statistics."""

        statistics.episodes_owned += task_stats.episodes_owned
        statistics.downloads_renamed += task_stats.downloads_renamed
        statistics.downloads_moved += task_stats.downloads_moved
        statistics.downloads_failed += task_stats.downloads_failed

    ############################################################################
    def _build_commands_for_task(
        self,
        old_fqn: str,
        new_fqn: str,
        conflict_result: ConflictResolutionResult,
    ) -> list[FileMutationCommand]:
        """Factory method for building mutation commands for one task."""

        commands: list[FileMutationCommand] = []
        if conflict_result.move_to_trash is not None:
            commands.append(MoveToTrashCommand(self._trash, conflict_result.move_to_trash))
        if not conflict_result.skip_rename:
            commands.append(RenameFileCommand(old_fqn, new_fqn))
        return commands

    ############################################################################
    def _execute_commands(self, commands: list[FileMutationCommand], statistics: Stats) -> None:
        """Execute prepared file-mutation commands in order."""

        for command in commands:
            if not command.execute(statistics):
                logger.error("task_execution: status=aborted reason=previous_failure")
                break

    ############################################################################
    def _finalize(self, statistics: Stats) -> None:
        """Finalize processing by handling trash maintenance and summary logging."""

        # Cleanup trash
        statistics.downloads_deleted = self._trash.cleanup()

        # List trash
        statistics.downloads_trash = self._trash.list()

        # Summary
        logger.info("run_summary: status=completed details=%s", statistics)
