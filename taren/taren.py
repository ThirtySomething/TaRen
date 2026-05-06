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
from typing import NamedTuple, Protocol

from taren.downloadlist import DownloadList
from taren.episode import Episode
from taren.episodelist import EpisodeList
from taren.stats import Stats
from taren.tarenconfig import TarenConfig
from taren.trash import Trash


class _DownloadTask(NamedTuple):
    filename: str
    episode: object


class _ConflictResolutionResult(NamedTuple):
    move_to_trash: str | None
    skip_rename: bool


class FileMutationCommand(Protocol):
    def execute(self, statistics: Stats) -> None:
        """Execute mutation and update statistics."""


class MoveToTrashCommand:
    def __init__(self, trash: Trash, file_path: str) -> None:
        self._trash: Trash = trash
        self._file_path: str = file_path

    def execute(self, statistics: Stats) -> None:
        self._trash.move(self._file_path)
        statistics.downloads_moved += 1


class RenameFileCommand:
    def __init__(self, source_file: str, destination_file: str) -> None:
        self._source_file: str = source_file
        self._destination_file: str = destination_file

    def execute(self, statistics: Stats) -> None:
        logging.info(
            "rename from [%s] to [%s] filename",
            self._source_file,
            self._destination_file,
        )
        os.rename(self._source_file, self._destination_file)
        statistics.downloads_renamed += 1


class ConflictResolutionStrategy(Protocol):
    def resolve(self, old_fqn: str, new_fqn: str) -> _ConflictResolutionResult:
        """Resolve rename conflicts and return follow-up actions."""


class SizeBasedConflictStrategy:
    """Default conflict strategy based on file size comparison."""

    def resolve(self, old_fqn: str, new_fqn: str) -> _ConflictResolutionResult:
        if not os.path.exists(new_fqn):
            return _ConflictResolutionResult(move_to_trash=None, skip_rename=False)

        size_old: int = os.stat(old_fqn).st_size
        size_new: int = os.stat(new_fqn).st_size

        if size_old == size_new:
            logging.info("file size equal, move file [%s] to trash", new_fqn)
            return _ConflictResolutionResult(move_to_trash=new_fqn, skip_rename=False)

        if size_old > size_new:
            logging.info(
                "one file smaller than the other one, move file [%s] to trash", new_fqn
            )
            return _ConflictResolutionResult(move_to_trash=new_fqn, skip_rename=False)

        logging.info(
            "one file smaller than the other one, move file [%s] to trash", old_fqn
        )
        return _ConflictResolutionResult(move_to_trash=old_fqn, skip_rename=True)


class TaRen:
    """
    Controlls the process of 'TAtort RENaming':
    - Download, parsing and list of Wiki page about episodes
    - Search for downloaded episodes
    - Perform renaming
    """

    ############################################################################
    def __init__(
        self,
        config: TarenConfig,
        conflict_strategy: ConflictResolutionStrategy | None = None,
    ) -> None:
        self._config: TarenConfig = config
        self._searchdir: str = self._sanitize_path(
            self._config.value_get("taren", "downloads")
        )
        self._pattern: str = self._config.value_get("taren", "pattern")
        self._extension: str = self._sanitize_extension(
            self._config.value_get("taren", "extension")
        )
        self._url: str = self._config.value_get("taren", "wiki")
        self._cachetime: int = int(self._config.value_get("taren", "maxcache"))
        self._trashage: int = int(self._config.value_get("taren", "trashage"))
        self._conflict_strategy: ConflictResolutionStrategy = (
            conflict_strategy or SizeBasedConflictStrategy()
        )
        self._trash: Trash = Trash(
            self._config.value_get("taren", "downloads"),
            self._config.value_get("taren", "trash"),
            self._trashage,
            self._config.value_get("taren", "trashignore"),
        )
        logging.debug("self._config [%s]", self._config)
        logging.debug("self._searchdir [%s]", self._searchdir)
        logging.debug("self._pattern [%s]", self._pattern)
        logging.debug("self._extension [%s]", self._extension)
        logging.debug("self._url [%s]", self._url)
        logging.debug("self._cachetime [%s]", self._cachetime)
        logging.debug("self._trashage [%s]", self._trashage)
        logging.debug(
            "self._conflict_strategy [%s]", type(self._conflict_strategy).__name__
        )

    ############################################################################
    def _sanitize_extension(self, extension: str) -> str:
        """
        Ensure extension starts with a dot
        """
        if not extension.startswith("."):
            extension = ".{}".format(extension)
        return extension

    ############################################################################
    def _sanitize_path(self, path: str) -> str:
        """
        Ensure searchdir ends with trailing slash
        """
        if not path.endswith(os.sep):
            path = "{}{}".format(path, os.sep)
        return path

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
        downloads_to_process: list[_DownloadTask] | None = self._collect_tasks(
            episode_list, statistics
        )
        if downloads_to_process is None:
            return
        self._process_tasks(downloads_to_process, statistics)
        self._finalize(statistics)

    ############################################################################
    def _preflight(self) -> bool:
        """Perform required pre-checks before processing."""

        # Check path of downloads
        if not os.path.exists(self._searchdir):
            logging.error(
                "Path [%s] does not exist or not found, abort", self._searchdir
            )
            return False

        return True

    ############################################################################
    def _load_episodes(self, statistics: Stats) -> EpisodeList:
        """Load episode metadata from configured source."""

        # Get list of episodes from web page
        ua: str = self._config.value_get("taren", "wiki_useragent")
        episode_list: EpisodeList = EpisodeList(
            self._pattern, self._url, self._cachetime, ua
        )
        episode_list.get_episodes()
        statistics.episodes_total = episode_list.get_episode_count()
        return episode_list

    ############################################################################
    def _collect_tasks(
        self, episode_list: EpisodeList, statistics: Stats
    ) -> list[_DownloadTask] | None:
        """Collect downloads that can be processed with known episode metadata."""

        # Get list of downloads from filesystem
        download_list: DownloadList = DownloadList(
            self._searchdir, self._pattern, self._extension
        )
        downloads: list[str] = download_list.get_filenames()
        statistics.downloads_total = len(downloads)

        # Check for trash
        if not self._trash.init():
            return None

        # Create list of downloads to process
        downloads_to_process: list[_DownloadTask] = []
        for current_download in downloads:
            episode: Episode = episode_list.find_episode(current_download)
            if episode.empty:
                continue
            downloads_to_process.append(
                _DownloadTask(filename=current_download, episode=episode)
            )
        logging.info("downloads_to_process [%s]", len(downloads_to_process))
        return downloads_to_process

    ############################################################################
    def _process_tasks(
        self, downloads_to_process: list[_DownloadTask], statistics: Stats
    ) -> None:
        """Apply rename and conflict handling for prepared tasks."""

        # Process downloads
        for current_download in downloads_to_process:
            new_fqn: str = os.path.join(
                self._searchdir,
                "{}{}".format(current_download.episode, self._extension),
            )
            old_fqn: str = os.path.join(self._searchdir, current_download.filename)

            if new_fqn == old_fqn:
                # Already processed episode
                statistics.episodes_owned += 1
                continue

            conflict_result: _ConflictResolutionResult = (
                self._conflict_strategy.resolve(old_fqn, new_fqn)
            )
            commands: list[FileMutationCommand] = self._build_commands_for_task(
                old_fqn, new_fqn, conflict_result
            )
            self._execute_commands(commands, statistics)

    ############################################################################
    def _build_commands_for_task(
        self,
        old_fqn: str,
        new_fqn: str,
        conflict_result: _ConflictResolutionResult,
    ) -> list[FileMutationCommand]:
        """Factory method for building mutation commands for one task."""

        commands: list[FileMutationCommand] = []
        if conflict_result.move_to_trash is not None:
            commands.append(
                MoveToTrashCommand(self._trash, conflict_result.move_to_trash)
            )
        if not conflict_result.skip_rename:
            commands.append(RenameFileCommand(old_fqn, new_fqn))
        return commands

    ############################################################################
    def _execute_commands(
        self, commands: list[FileMutationCommand], statistics: Stats
    ) -> None:
        """Execute prepared file-mutation commands in order."""

        for command in commands:
            command.execute(statistics)

    ############################################################################
    def _finalize(self, statistics: Stats) -> None:
        """Finalize processing by handling trash maintenance and summary logging."""

        # Cleanup trash
        statistics.downloads_deleted = self._trash.cleanup()

        # List trash
        statistics.downloads_trash = self._trash.list()

        # Summary
        logging.info("summary: %s", statistics)
