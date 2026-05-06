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
from typing import NamedTuple

from taren.downloadlist import DownloadList
from taren.episode import Episode
from taren.episodelist import EpisodeList
from taren.stats import Stats
from taren.tarenconfig import TarenConfig
from taren.trash import Trash


class _DownloadTask(NamedTuple):
    filename: str
    episode: object


class TaRen:
    """
    Controlls the process of 'TAtort RENaming':
    - Download, parsing and list of Wiki page about episodes
    - Search for downloaded episodes
    - Perform renaming
    """

    ############################################################################
    def __init__(self, config: TarenConfig) -> None:
        self._config: TarenConfig = config
        self._searchdir: str = self._sanitize_path(self._config.value_get("taren", "downloads"))
        self._pattern: str = self._config.value_get("taren", "pattern")
        self._extension: str = self._sanitize_extension(self._config.value_get("taren", "extension"))
        self._url: str = self._config.value_get("taren", "wiki")
        self._cachetime: int = int(self._config.value_get("taren", "maxcache"))
        self._trashage: int = int(self._config.value_get("taren", "trashage"))
        self._trash: Trash = Trash(
            self._config.value_get("taren", "downloads"), self._config.value_get("taren", "trash"), self._trashage, self._config.value_get("taren", "trashignore")
        )
        logging.debug("self._config [%s]", self._config)
        logging.debug("self._searchdir [%s]", self._searchdir)
        logging.debug("self._pattern [%s]", self._pattern)
        logging.debug("self._extension [%s]", self._extension)
        logging.debug("self._url [%s]", self._url)
        logging.debug("self._cachetime [%s]", self._cachetime)
        logging.debug("self._trashage [%s]", self._trashage)

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

        # Check path of downloads
        if not os.path.exists(self._searchdir):
            logging.error("Path [%s] does not exist or not found, abort", self._searchdir)
            return

        # Object to handle statistics
        statistics: Stats = Stats()

        # Get list of episodes from web page
        ua: str = self._config.value_get("taren", "wiki_useragent")
        episode_list: EpisodeList = EpisodeList(self._pattern, self._url, self._cachetime, ua)
        episode_list.get_episodes()
        statistics.episodes_total = episode_list.get_episode_count()

        # Get list of downloads from filesystem
        download_list: DownloadList = DownloadList(self._searchdir, self._pattern, self._extension)
        downloads: list[str] = download_list.get_filenames()
        statistics.downloads_total = len(downloads)

        # Check for trash
        if not self._trash.init():
            return

        # Create list of downloads to process
        downloads_to_process: list[_DownloadTask] = []
        for current_download in downloads:
            episode: Episode = episode_list.find_episode(current_download)
            if episode.empty:
                continue
            downloads_to_process.append(_DownloadTask(filename=current_download, episode=episode))
        logging.info("downloads_to_process [%s]", len(downloads_to_process))

        # Process downloads
        for current_download in downloads_to_process:
            new_fqn: str = os.path.join(self._searchdir, "{}{}".format(current_download.episode, self._extension))
            old_fqn: str = os.path.join(self._searchdir, current_download.filename)

            if new_fqn == old_fqn:
                # Already processed episode
                statistics.episodes_owned += 1
                continue

            if os.path.exists(new_fqn):
                # New episode already exists
                size_old: int = os.stat(old_fqn).st_size
                size_new: int = os.stat(new_fqn).st_size

                if size_old == size_new:
                    # Episode and download are equal
                    logging.info("file size equal, move file [%s] to trash", new_fqn)
                    # Move to trash
                    self._trash.move(new_fqn)
                    statistics.downloads_moved += 1

                elif size_old > size_new:
                    # Episode is greater than download
                    logging.info("one file smaller than the other one, move file [%s] to trash", new_fqn)
                    # Move to trash
                    self._trash.move(new_fqn)
                    statistics.downloads_moved += 1

                else:
                    # Download is greater than episode
                    logging.info("one file smaller than the other one, move file [%s] to trash", old_fqn)
                    # Move to trash
                    self._trash.move(old_fqn)
                    statistics.downloads_moved += 1
                    continue

            # Rename download to name of episode
            logging.info("rename from [%s] to [%s] filename", old_fqn, new_fqn)
            os.rename(old_fqn, new_fqn)
            statistics.downloads_renamed += 1

        # Cleanup trash
        statistics.downloads_deleted = self._trash.cleanup()

        # List trash
        statistics.downloads_trash = self._trash.list()

        # Summary
        logging.info("summary: %s", statistics)
