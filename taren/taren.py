'''
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
'''

import logging
import os

from taren.downloadlist import DownloadList
from taren.episodelist import EpisodeList
from taren.trash import Trash


class TaRen:
    '''
    Controlls the process of 'TAtort RENaming':
    - Download, parsing and list of Wiki page about episodes
    - Search for downloaded episodes
    - Perform renaming
    '''

    def __init__(self: object, searchdir: str, pattern: str, extension: str, url: str, cachetime: int, trash: str, trashage: int) -> None:
        self._searchdir: str = self._sanitize_path(searchdir)
        self._pattern: str = pattern
        self._extension: str = self._sanitize_extension(extension)
        self._url: str = url
        self._cachetime: int = cachetime
        self._trash: str = os.path.join(self._searchdir, trash)
        self._trashage: int = trashage
        self._trash_new: Trash = Trash(searchdir, trash, self._trashage)
        logging.debug('searchdir [%s]', '{}'.format(searchdir))
        logging.debug('pattern [%s]', '{}'.format(pattern))
        logging.debug('extension [%s]', '{}'.format(extension))
        logging.debug('url [%s]', '{}'.format(url))
        logging.debug('cachetime [%s]', '{}'.format(cachetime))
        logging.debug('trash [%s]', '{}'.format(self._trash))
        logging.debug('trashage [%s]', '{}'.format(self._trashage))

    def _sanitize_path(self: object, path: str) -> str:
        '''
        Ensure searchdir ends with trailing slash
        '''
        if not path.endswith('\\'):
            path = '{}\\'.format(path)
        return path

    def _sanitize_extension(self: object, extension: str) -> str:
        '''
        Ensure extension starts with a dot
        '''
        if not extension.startswith('.'):
            extension = '.{}'.format(extension)
        return extension

    def rename_process(self: object) -> None:
        '''
        Controls the complete process:
        - Get website content about the episodes
        - Build internal list about episodes
        - Find affected downloads
        '''
        # Check path of downloads
        if not os.path.exists(self._searchdir):
            logging.error('Path [%s] does not exist or not found, abort', '{}'.format(self._searchdir))
            return

        # Get list of episodes
        episode_list: EpisodeList = EpisodeList(self._pattern, self._url, self._cachetime)
        episode_list.get_episodes()

        # Get list of downloads
        download_list: DownloadList = DownloadList(self._searchdir, self._pattern, self._extension)
        downloads: list[str] = download_list.get_filenames()

        # Check for trash
        if not self._trash_new.init():
            return False

        # Create list of downloads to process
        downloads_to_process: list[str] = []
        for current_download in downloads:
            episode = episode_list.find_episode(current_download)
            if episode.empty:
                continue
            downloads_to_process.append([current_download, episode])
            logging.debug('added to process list: [%s] <> [%s]', '{}'.format(current_download), '{}'.format(episode))
        logging.info('downloads_to_process [%s]', '{}'.format(len(downloads_to_process)))

        # Process downloads
        deleted: int = 0
        trash: int = 0
        renamed: int = 0
        skipped: int = 0
        total: int = 0
        for current_task in downloads_to_process:
            total = total + 1
            new_fqn: str = os.path.join(self._searchdir, '{}{}'.format(current_task[1], self._extension))
            old_fqn: str = os.path.join(self._searchdir, current_task[0])

            if new_fqn == old_fqn:
                # Already processed episode
                logging.debug('filenames identical, skip file [%s]', '{}'.format(old_fqn))
                skipped = skipped + 1
                continue
            if os.path.exists(new_fqn):
                # New episode already exists
                logging.debug('file already exists [%s]', '{}'.format(new_fqn))
                size_old: int = os.stat(old_fqn).st_size
                size_new: int = os.stat(new_fqn).st_size

                if size_old == size_new:
                    # Episode and download are equal
                    logging.info('file size equal, move file [%s] to trash', '{}'.format(new_fqn))
                    # Move to trash
                    self._trash_new.move(new_fqn)
                    trash = trash + 1

                if size_old > size_new:
                    # Episode is greater than download
                    logging.info('one file smaller than the other one, move file [%s] to trash', '{}'.format(new_fqn))
                    # Move to trash
                    self._trash_new.move(new_fqn)
                    trash = trash + 1

                if size_old < size_new:
                    # Download is greater than episode
                    logging.info('one file smaller than the other one, move file [%s] to trash', '{}'.format(old_fqn))
                    # Move to trash
                    self._trash_new.move(old_fqn)
                    trash = trash + 1
                    continue

            # Rename download to name of episode
            logging.info('rename from [%s] to [%s] filename', '{}'.format(old_fqn), '{}'.format(new_fqn))
            os.rename(old_fqn, new_fqn)
            renamed = renamed + 1

        # Cleanup trash
        deleted = self._trash_new.cleanup()

        # List trash
        self._trash_new.list()

        # Summary
        logging.info('summary: files total [%s], skipped [%s], renamed [%s], trash [%s], deleted [%s]', '{}'.format(total), '{}'.format(skipped), '{}'.format(renamed), '{}'.format(trash), '{}'.format(deleted))
