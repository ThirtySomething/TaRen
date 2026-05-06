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
from typing import Protocol

from bs4 import BeautifulSoup
from bs4.element import Tag

from taren.episode import Episode
from taren.websitecache import HttpFetchPolicy, WebSiteCache


class EpisodeSource(Protocol):
    def fetch(self) -> str:
        """Retrieve raw episode source content."""


class CachedHtmlEpisodeSource:
    """Adapter for retrieving episode HTML via website cache."""

    def __init__(
        self,
        pattern: str,
        url: str,
        cachetime: int,
        useragent: str,
        fetch_policy: HttpFetchPolicy | None = None,
    ) -> None:
        self._cache: WebSiteCache = WebSiteCache(
            pattern,
            url,
            cachetime,
            useragent,
            fetch_policy=fetch_policy,
        )

    def fetch(self) -> str:
        return self._cache.get_website_from_cache()


class EpisodeList:
    """
    Extract from given website the episode list
    """

    ############################################################################
    def __init__(
        self,
        pattern: str,
        url: str,
        cachetime: int,
        useragent: str,
        fetch_policy: HttpFetchPolicy | None = None,
        episode_source: EpisodeSource | None = None,
    ) -> None:
        self._pattern: str = pattern
        self._url: str = url
        self._cachetime: int = cachetime
        self._useragent: str = useragent
        self._episode_source: EpisodeSource = episode_source or CachedHtmlEpisodeSource(
            pattern,
            url,
            cachetime,
            useragent,
            fetch_policy=fetch_policy,
        )
        self._episodes: list[Episode] = []
        logging.debug("pattern [%s]", pattern)
        logging.debug("url [%s]", url)
        logging.debug("cachetime [%s]", cachetime)
        logging.debug("useragent [%s]", useragent)

    ############################################################################
    def _build_list_of_episodes(self, raw_data: list[Tag]) -> list[Episode]:
        """
        Extract episodes from episode list
        """
        episodes: list[Episode] = []
        # For each HTML table row aka raw episode data
        for table_row in raw_data:
            # Extract all columns as cell
            table_cells: list[Tag] = table_row.find_all("td")
            if len(table_cells) < 6:
                logging.debug("skip malformed episode table row with [%s] cells", len(table_cells))
                continue
            # Get content of cells
            episode_data: list[str] = [i.text.replace("\n", "") for i in table_cells]
            # Create a new and empty episode
            current_episode: Episode = Episode()
            # Parse raw data into episode object
            current_episode.parse(episode_data)
            # When episode was successfully parsed, add to list
            if not current_episode.empty:
                episodes.append(current_episode)
        # Return list of episodes
        episodes.sort()
        return episodes

    ############################################################################
    def _parse_website(self, websitecontent: str) -> list[Episode]:
        """
        Build internal list about episodes based on website content.
        """
        if not websitecontent.strip():
            logging.warning("episode list website content is empty")
            return []
        # Parse website using BeautifulSoup
        websitedata: BeautifulSoup = BeautifulSoup(websitecontent, "html.parser")
        # Get table with episodes - there is only one tables
        table = websitedata.find("table")
        if table is None:
            logging.warning("episode list table not found in website content")
            return []
        # Get raw episode data from table data row
        rows: list[Tag] = table.find_all("tr")
        # Build list of episodes for all rows
        episodes: list[Episode] = self._build_list_of_episodes(rows)
        return episodes

    ############################################################################
    def _read_website(self) -> str:
        """
        Retrieve website content via configured episode source
        """
        return self._episode_source.fetch()

    ############################################################################
    def find_episode(self, filename: str) -> Episode:
        """
        Find episode in list
        """
        # Create empty episode
        episode: Episode = Episode.empty_instance()
        # Loop over all episodes
        for current_episode in self._episodes:
            # Does filename match episode
            if current_episode.matches(filename):
                # Memorize episode and abort loop
                episode = current_episode
                break

        # Return either empty episode or found episode
        return episode

    ############################################################################
    def get_episode_count(self) -> int:
        return len(self._episodes)

    ############################################################################
    def get_episodes(self) -> None:
        """
        Read website and extract episodes, return them as list.
        """
        # Get website content
        websitecontent: str = self._read_website()
        # Parse website
        self._episodes = self._parse_website(websitecontent)
        logging.info("total number of episodes [%s]", len(self._episodes))
