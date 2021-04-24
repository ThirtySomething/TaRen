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

    def __init__(self, searchdir, pattern, extension, url, cachetime, trash, trashage):
        self.searchdir = searchdir
        self.pattern = pattern
        self.extension = extension
        self.url = url
        self.cachetime = cachetime
        self.trash = os.path.join(self.searchdir, trash)
        self.trashage = trashage
        if not self.extension.startswith('.'):
            self.extension = '.{}'.format(self.extension)
        if not self.searchdir.endswith('\\'):
            self.searchdir = '{}\\'.format(self.searchdir)
        logging.debug('searchdir [%s]', '{}'.format(searchdir))
        logging.debug('pattern [%s]', '{}'.format(pattern))
        logging.debug('extension [%s]', '{}'.format(extension))
        logging.debug('url [%s]', '{}'.format(url))
        logging.debug('cachetime [%s]', '{}'.format(cachetime))
        logging.debug('trash [%s]', '{}'.format(self.trash))
        logging.debug('trashage [%s]', '{}'.format(self.trashage))

    def trash_create(self):
        if not os.path.exists(self.trash):
            try:
                os.mkdir(self.trash)
                logging.debug('Directory [%s] created', '{}'.format(self.trash))
            except OSError:
                logging.error('Creation of the directory [%s] failed, abort', '{}'.format(self.trash))
                return False
        else:
            logging.info('Directory [%s] alread exists', '{}'.format(self.trash))
        return True

    def trash_cleanup(self):
        now = time.time()
        logging.info('Delete files older than [%s] days from bin [%s]', '{}'.format(self.trashage), '{}'.format(self.trash))
        for filename in os.listdir(self.trash):
            if os.path.getmtime(os.path.join(self.trash, filename)) < now - self.trashage * 86400:
                if os.path.isfile(os.path.join(self.trash, filename)):
                    os.remove(os.path.join(self.trash, filename))
                    logging.info('Delete file [%s]', '{}'.format(filename))

    def trash_move(self, src, dst):
        logging.debug('Move file [%s] to [%s]', '{}'.format(src), '{}'.format(dst))
        os.rename(src, dst)
        now = time.time()
        logging.debug('Set access/modified timestamp of [%s] to [%s]', '{}'.format(dst), '{}'.format(now))
        os.utime(dst,(now, now))

    def rename_process(self):
        '''
        Controls the complete process:
        - Get website content about the episodes
        - Build internal list about episodes
        - Find affected downloads
        '''
        episode_list = EpisodeList(self.pattern, self.url, self.cachetime)
        episode_list.get_episodes()

        download_list = DownloadList(self.searchdir, self.pattern, self.extension)
        downloads = download_list.get_filenames()

        if not self.trash_create():
            return False

        downloads_to_process = []
        for current_download in downloads:
            episode = episode_list.find_episode(current_download)
            if episode.empty:
                continue
            downloads_to_process.append([current_download, episode])
            logging.debug('added to process list: [%s] <> [%s]', '{}'.format(current_download), '{}'.format(episode))
        logging.info('downloads_to_process %s', '{}'.format(len(downloads_to_process)))

        renamed = 0
        skipped = 0
        total = 0
        deleted = 0
        for current_task in downloads_to_process:
            total = total + 1
            new_fqn = os.path.join(self.searchdir, '{}{}'.format(current_task[1], self.extension))
            old_fqn = os.path.join(self.searchdir, current_task[0])

            if new_fqn == old_fqn:
                logging.debug('filenames identical, skip file [%s]', '{}'.format(old_fqn))
                skipped = skipped + 1
                continue
            if path.exists(new_fqn):
                logging.debug('file already exists [%s]', '{}'.format(new_fqn))
                size_old = os.stat(old_fqn).st_size
                size_new = os.stat(new_fqn).st_size
                if size_old == size_new:
                    logging.info('file size equal, delete file [%s]', '{}'.format(new_fqn))
                    dst_fqn = os.path.join(self.trash, '{}{}'.format(current_task[1], self.extension))
                    self.trash_move(new_fqn, dst_fqn)
                    deleted = deleted + 1
                if size_old > size_new:
                    logging.info('one file smaller than the other one, delete file [%s]', '{}'.format(new_fqn))
                    dst_fqn = os.path.join(self.trash, '{}{}'.format(current_task[1], self.extension))
                    self.trash_move(new_fqn, dst_fqn)
                    deleted = deleted + 1
                if size_old < size_new:
                    logging.info('one file smaller than the other one, delete file [%s]', '{}'.format(old_fqn))
                    dst_fqn = os.path.join(self.trash, current_task[0])
                    self.trash_move(old_fqn, dst_fqn)
                    deleted = deleted + 1
                    continue

            logging.info('rename from [%s] to [%s] filename', '{}'.format(old_fqn), '{}'.format(new_fqn))
            os.rename(old_fqn, new_fqn)
            renamed = renamed + 1
        logging.info('files total [%s], skipped [%s], renamed [%s], deleted [%s]', '{}'.format(total), '{}'.format(skipped), '{}'.format(renamed), '{}'.format(deleted))
        self.trash_cleanup()
