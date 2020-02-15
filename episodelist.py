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
from bs4 import BeautifulSoup
from episode import Episode
from websitecache import WebSiteCache

class EpisodeList:
    '''
    Extract from given website the episode list
    '''
    def __init__(self, pattern, url, cachetime):
        self.pattern = pattern
        self.url = url
        self.cachetime = cachetime
        self.episodes = []
        logging.debug('pattern [%s]', '{}'.format(pattern))
        logging.debug('url [%s]', '{}'.format(url))
        logging.debug('cachetime [%s]', '{}'.format(cachetime))

    def _read_website(self):
        '''
        Retrieve website via cache
        '''
        cache = WebSiteCache(self.pattern, self.url, self.cachetime)
        return cache.get_website_from_cache()

    def _parse_website(self, websitecontent):
        '''
        Build internal list about episodes based on website content.
        '''
        websitedata = BeautifulSoup(websitecontent, 'html.parser')
        table = websitedata.find('table')
        rows = table.find_all('tr')
        episodes = self._build_list_of_episodes(rows)
        return episodes

    def _build_list_of_episodes(self, raw_data):
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
                logging.debug('episode [%s]', '{}'.format(current_episode))
        return episodes

    def get_episodes(self):
        '''
        Read website and extract episodes, return them as list.
        '''
        websitecontent = self._read_website()
        self.episodes = self._parse_website(websitecontent)
        logging.info('total number of episodes [%s]', '{}'.format(len(self.episodes)))

    def find_episode(self, filename):
        '''
        Find episode in list
        '''
        episode = Episode()
        for current_episode in self.episodes:
            if current_episode.matches(filename):
                episode = current_episode
                break

        if episode.empty:
            logging.info('no match for filename [%s]', '{}'.format(filename))
        else:
            logging.debug('filename [%s] matches episode_name [%s]', '{}'.format(filename), '{}'.format(episode.episode_name))

        return episode
