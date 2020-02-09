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
import fnmatch
import os
from bs4 import BeautifulSoup
from episode import Episode
from wikicache import WikiCache

class TaRen:
    '''
    Controlls the process of 'TAtort RENaming':
    - Download, parsing and list of Wiki page about episodes
    - Search for downloaded episodes
    - Perform renaming
    '''
    def __init__(self, searchdir, pattern, extension, url, cachetime):
        self.searchdir = searchdir
        self.pattern = pattern
        self.extension = extension
        self.url = url
        self.cachetime = cachetime
        self.episodes = []
        if not self.extension.startswith('.'):
            self.extension = '.{}'.format(self.extension)
        logging.debug('searchdir [%s]', '{}'.format(searchdir))
        logging.debug('pattern [%s]', '{}'.format(pattern))
        logging.debug('extension [%s]', '{}'.format(extension))
        logging.debug('url [%s]', '{}'.format(url))
        logging.debug('cachetime [%s]', '{}'.format(cachetime))

    def rename_process(self):
        '''
        Controls the complete process:
        - Get website content about the episodes
        - Build internal list about episodes
        - Find affected downloads
        '''
        websitecontent = self.read_website()
        self.parse_website(websitecontent)
        # files = self.collect_filenames()
        # logging.debug('files [{}]'.format(files))
        # logging.debug('content [{}]'.format(self.content))

    def collect_filenames(self):
        '''
        Retrieve list of affected files
        '''
        searchpattern = '*{}*{}'.format(self.pattern, self.extension)
        files = fnmatch.filter(os.listdir(self.searchdir), searchpattern)
        return files

    def read_website(self):
        '''
        Retrieve website via cache
        '''
        cache = WikiCache(self.pattern, self.url, self.cachetime)
        return cache.get_website_from_cache()

    def parse_website(self, websitecontent):
        '''
        Build internal list about episodes based on website content.
        '''
        websitedata = BeautifulSoup(websitecontent, 'html.parser')
        table = websitedata.find('table')
        rows = table.find_all('tr')
        self.episodes = self.build_list_of_episodes(rows)

    def build_list_of_episodes(self, raw_data):
        '''
        Extract episodes from episode list
        '''
        episodes = []
        for table_row in raw_data:
            table_cells = table_row.find_all('td')
            episode_data = [i.text for i in table_cells]
            current_episode = Episode()
            current_episode.parse(episode_data)
            if not current_episode.empty:
                episodes.append(current_episode)
                logging.info('episode [%s]', '{}'.format(current_episode))
        logging.info('total number of episodes [%s]', '{}'.format(len(episodes)))
        return episodes
