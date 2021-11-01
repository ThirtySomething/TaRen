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
import time
from os import path
from .episodelist import EpisodeList
from .downloadlist import DownloadList


class TaRen:
    '''
    Controlls the process of 'TAtort RENaming':
    - Download, parsing and list of Wiki page about episodes
    - Search for downloaded episodes
    - Perform renaming
    '''

    def __init__(self: object, searchdir: str, pattern: str, extension: str, url: str, cachetime: int, trash: str, trashage: int) -> None:
        self.searchdir: str = searchdir
        self.pattern: str = pattern
        self.extension: str = extension
        self.url: str = url
        self.cachetime: int = cachetime
        self.trash: str = os.path.join(self.searchdir, trash)
        self.trashage: int = trashage
        # Ensure extension starts with a dot
        if not self.extension.startswith('.'):
            self.extension = '.{}'.format(self.extension)
        # Ensure searchdir ends with trailing slash
        if not self.searchdir.endswith('\\'):
            self.searchdir = '{}\\'.format(self.searchdir)
        logging.debug('searchdir [%s]', '{}'.format(searchdir))
        logging.debug('pattern [%s]', '{}'.format(pattern))
        logging.debug('extension [%s]', '{}'.format(extension))
        logging.debug('url [%s]', '{}'.format(url))
        logging.debug('cachetime [%s]', '{}'.format(cachetime))
        logging.debug('trash [%s]', '{}'.format(self.trash))
        logging.debug('trashage [%s]', '{}'.format(self.trashage))

    def _trash_create(self: object) -> bool:
        '''
        Ensure existence of the trash folder
        '''
        if not os.path.exists(self.trash):
            try:
                # Create missing folder
                os.mkdir(self.trash)
                logging.debug('Directory [%s] created', '{}'.format(self.trash))
            except OSError:
                logging.error('Creation of the directory [%s] failed, abort', '{}'.format(self.trash))
                return False
        else:
            logging.debug('Directory [%s] alread exists', '{}'.format(self.trash))
        return True

    def _trash_cleanup(self: object) -> int:
        '''
        Delete files from trah older than configured age
        '''
        deleted: int = 0
        # Calculate maximum age
        maxage: int = time.time() - self.trashage * 86400
        logging.info('Delete files older than [%s] days from trash [%s]', '{}'.format(self.trashage), '{}'.format(self.trash))
        # Loop over all in trash
        for filename in os.listdir(self.trash):
            # Build FQN
            fname: str = os.path.join(self.trash, filename)
            # Check only files
            if os.path.isfile(fname):
                # Check age of file
                if os.path.getmtime(fname) < maxage:
                    # Perform deletion
                    os.remove(fname)
                    logging.info('Delete file [%s]', '{}'.format(filename))
                    deleted = deleted + 1
        return deleted

    def _trash_list(self: object) -> None:
        '''
        List all files from trah
        '''
        logging.info('List files from trash [%s]', '{}'.format(self.trash))
        # Loop over all in trash
        for filename in os.listdir(self.trash):
            # Build FQN
            fname: str = os.path.join(self.trash, filename)
            # Check only files
            if os.path.isfile(fname):
                # List file
                logging.info('File [%s]', '{}'.format(filename))

    def _trash_move(self: object, src: str, dst: str) -> None:
        '''
        Move file to trash and modify file date to deletion timestamp
        '''
        # Move file to trash
        logging.debug('Move file [%s] to [%s]', '{}'.format(src), '{}'.format(dst))
        os.rename(src, dst)
        # Modify timestamp
        now: float = time.time()
        logging.debug('Set access/modified timestamp of [%s] to [%s]', '{}'.format(dst), '{}'.format(now))
        os.utime(dst, (now, now))

    def rename_process(self: object) -> None:
        '''
        Controls the complete process:
        - Get website content about the episodes
        - Build internal list about episodes
        - Find affected downloads
        '''
        # Get list of episodes
        episode_list: EpisodeList = EpisodeList(self.pattern, self.url, self.cachetime)
        episode_list.get_episodes()

        # Get list of downloads
        download_list: DownloadList = DownloadList(self.searchdir, self.pattern, self.extension)
        downloads: list[str] = download_list.get_filenames()

        # Check for trash
        if not self._trash_create():
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
            new_fqn: str = os.path.join(self.searchdir, '{}{}'.format(current_task[1], self.extension))
            old_fqn: str = os.path.join(self.searchdir, current_task[0])

            if new_fqn == old_fqn:
                # Already processed episode
                logging.debug('filenames identical, skip file [%s]', '{}'.format(old_fqn))
                skipped = skipped + 1
                continue
            if path.exists(new_fqn):
                # New episode already exists
                logging.debug('file already exists [%s]', '{}'.format(new_fqn))
                size_old: int = os.stat(old_fqn).st_size
                size_new: int = os.stat(new_fqn).st_size

                if size_old == size_new:
                    # Episode and download are equal
                    logging.info('file size equal, move file [%s] to trash', '{}'.format(new_fqn))
                    # Move to trash
                    dst_fqn: str = os.path.join(self.trash, '{}{}'.format(current_task[1], self.extension))
                    self._trash_move(new_fqn, dst_fqn)
                    trash = trash + 1

                if size_old > size_new:
                    # Episode is greater than download
                    logging.info('one file smaller than the other one, move file [%s] to trash', '{}'.format(new_fqn))
                    # Move to trash
                    dst_fqn: str = os.path.join(self.trash, '{}{}'.format(current_task[1], self.extension))
                    self._trash_move(new_fqn, dst_fqn)
                    trash = trash + 1

                if size_old < size_new:
                    # Download is greater than episode
                    logging.info('one file smaller than the other one, move file [%s] to trash', '{}'.format(old_fqn))
                    # Move to trash
                    dst_fqn: str = os.path.join(self.trash, current_task[0])
                    self._trash_move(old_fqn, dst_fqn)
                    trash = trash + 1
                    continue

            # Rename download to name of episode
            logging.info('rename from [%s] to [%s] filename', '{}'.format(old_fqn), '{}'.format(new_fqn))
            os.rename(old_fqn, new_fqn)
            renamed = renamed + 1

        # Cleanup trash
        deleted = self._trash_cleanup()

        # List trash
        self._trash_list()

        # Summary
        logging.info('summary: files total [%s], skipped [%s], renamed [%s], trash [%s], deleted [%s]', '{}'.format(total), '{}'.format(skipped), '{}'.format(renamed), '{}'.format(trash), '{}'.format(deleted))
