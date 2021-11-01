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

    def __init__(self: object, pattern: str, url: str, cachetime: int) -> None:
        self.pattern: str = pattern
        self.url: str = url
        self.cachetime: int = cachetime
        self.episodes: list[Episode] = []
        logging.debug('pattern [%s]', '{}'.format(pattern))
        logging.debug('url [%s]', '{}'.format(url))
        logging.debug('cachetime [%s]', '{}'.format(cachetime))

    def _read_website(self: object) -> str:
        '''
        Retrieve website via cache
        '''
        # Get website content from cache handler
        cache: WebSiteCache = WebSiteCache(self.pattern, self.url, self.cachetime)
        return cache.get_website_from_cache()

    def _parse_website(self: object, websitecontent: str) -> list[Episode]:
        '''
        Build internal list about episodes based on website content.
        '''
        # Parse website using BeautifulSoup
        websitedata: BeautifulSoup = BeautifulSoup(websitecontent, 'html.parser')
        # Get table with episodes - there is only one tables
        table: str = websitedata.find('table')
        # Get raw episode data from table data row
        rows: list[str] = table.find_all('tr')
        # Build list of episodes for all rows
        episodes: list[Episode] = self._build_list_of_episodes(rows)
        return episodes

    def _build_list_of_episodes(self: object, raw_data: str) -> list[Episode]:
        '''
        Extract episodes from episode list
        '''
        episodes: list[Episode] = []
        # For each HTML table row aka raw episode data
        for table_row in raw_data:
            # Extract all columns as cell
            table_cells: list[str] = table_row.find_all('td')
            # Get content of cells
            episode_data: list[str] = [i.text.replace('\n', '') for i in table_cells]
            # Create a new and empty episode
            current_episode: Episode = Episode()
            # Parse raw data into episode object
            current_episode.parse(episode_data)
            # When episode was successfully parsed, add to list
            if not current_episode.empty:
                episodes.append(current_episode)
                logging.debug('episode [%s]', '{}'.format(current_episode))
        # Return list of episodes
        episodes.sort()
        return episodes

    def get_episodes(self: object) -> None:
        '''
        Read website and extract episodes, return them as list.
        '''
        # Get website content
        websitecontent: str = self._read_website()
        # Parse website
        self.episodes = self._parse_website(websitecontent)
        logging.info('total number of episodes [%s]', '{}'.format(len(self.episodes)))

    def find_episode(self: object, filename: str) -> Episode:
        '''
        Find episode in list
        '''
        # Create empty episode
        episode: Episode = Episode()
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
