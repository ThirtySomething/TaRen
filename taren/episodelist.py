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
from .episode import Episode
from .websitecache import WebSiteCache


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
        # Get website content from cache handler
        cache = WebSiteCache(self.pattern, self.url, self.cachetime)
        return cache.get_website_from_cache()

    def _parse_website(self, websitecontent):
        '''
        Build internal list about episodes based on website content.
        '''
        # Parse website using BeautifulSoup
        websitedata = BeautifulSoup(websitecontent, 'html.parser')
        # Get table with episodes - there is only one tables
        table = websitedata.find('table')
        # Get raw episode data from table data row
        rows = table.find_all('tr')
        # Build list of episodes for all rows
        episodes = self._build_list_of_episodes(rows)
        return episodes

    def _build_list_of_episodes(self, raw_data):
        '''
        Extract episodes from episode list
        '''
        episodes = []
        # For each HTML table row aka raw episode data
        for table_row in raw_data:
            # Extract all columns as cell
            table_cells = table_row.find_all('td')
            # Get content of cells
            episode_data = [i.text.replace('\n', '') for i in table_cells]
            # Create a new and empty episode
            current_episode = Episode()
            # Parse raw data into episode object
            current_episode.parse(episode_data)
            # When episode was successfully parsed, add to list
            if not current_episode.empty:
                episodes.append(current_episode)
                logging.debug('episode [%s]', '{}'.format(current_episode))
        # Return list of episodes
        episodes.sort()
        return episodes

    def get_episodes(self):
        '''
        Read website and extract episodes, return them as list.
        '''
        # Get website content
        websitecontent = self._read_website()
        # Parse website
        self.episodes = self._parse_website(websitecontent)
        logging.info('total number of episodes [%s]', '{}'.format(len(self.episodes)))

    def find_episode(self, filename):
        '''
        Find episode in list
        '''
        # Create empty episode
        episode = Episode()
        # Loop over all episodes
        for current_episode in self.episodes:
            # Does filename match episode
            if current_episode.matches(filename):
                # Memorize episode and abort loop
                episode = current_episode
                break

        # Check episode for logging data
        if episode.empty:
            logging.info('no match for filename [%s]', '{}'.format(filename))
        else:
            logging.debug('filename [%s] matches episode_name [%s]', '{}'.format(filename), '{}'.format(episode.episode_name))

        # Return either empty episode or found episode
        return episode
