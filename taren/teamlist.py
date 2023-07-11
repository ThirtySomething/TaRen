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

from bs4 import BeautifulSoup

from taren.episode import Episode
from taren.team import Team
from taren.websitecache import WebSiteCache


class TeamList:
    """
    Extract from given website the team list
    """

    ############################################################################
    def __init__(self: object, listname: str, url: str, cachetime: int) -> None:
        self._listname: str = listname
        self._url: str = url
        self._cachetime: int = cachetime
        self._teams: list[Team] = []
        logging.debug("listname [{}]".format(listname))
        logging.debug("url [{}]".format(url))
        logging.debug("cachetime [{}]".format(cachetime))

    ############################################################################
    def _build_list_of_teams(self: object, raw_data: str) -> list[Team]:
        """
        Extract teams from team list
        """
        teams: list[Team] = []
        # For each HTML table row aka raw episode data
        for table_row in raw_data:
            # Extract all columns as cell
            table_cells: list[str] = table_row.find_all("td")
            # Get content of cells
            team_data: list[str] = [i.text.replace("\n", "") for i in table_cells]
            # Create a new and empty episode
            current_team: Team = Team()
            # Parse raw data into episode object
            current_team.parse(team_data)
            # When team was successfully parsed, add to list
            if not current_team.empty:
                teams.append(current_team)
                logging.debug("team [{}]".format(current_team))
        # Return list of teams
        teams.sort()
        return teams

    ############################################################################
    def _parse_website(self: object, websitecontent: str) -> list[Team]:
        """
        Build internal list about teams based on website content.
        """
        # Parse website using BeautifulSoup
        websitedata: BeautifulSoup = BeautifulSoup(websitecontent, "html.parser")
        # Get table with teams - there is only one tables
        table: str = websitedata.find("table")
        # Get raw team data from table data row
        rows: list[str] = table.find_all("tr")
        # Build list of episodes for all rows
        teams: list[Team] = self._build_list_of_teams(rows)
        return teams

    ############################################################################
    def _read_website(self: object) -> str:
        """
        Retrieve website via cache
        """
        # Get website content from cache handler
        cache: WebSiteCache = WebSiteCache(self._listname, self._url, self._cachetime)
        return cache.get_website_from_cache()

    ############################################################################
    def find_team(self: object, episode: Episode) -> Team:
        """
        Find team in list
        """
        # Create empty team
        team: Team = Team()
        # Loop over all teams
        for current_team in self._teams:
            # Does episode match team
            if current_team.matches(episode):
                # Memorize team and abort loop
                team = current_team
                break

        # Check team for logging data
        if team.empty:
            logging.info("no match for episode [{}]".format(episode))
        else:
            logging.debug("episode [{}] matches team [{}]".format(episode, team))

        # Return either empty team or found team
        return team

    ############################################################################
    def get_team_count(self: object) -> int:
        return len(self._teams)

    ############################################################################
    def get_teams(self: object) -> None:
        """
        Read website and extract teams, return them as list.
        """
        # Get website content
        websitecontent: str = self._read_website()
        # Parse website
        self._teams = self._parse_website(websitecontent)
        logging.info("total number of teams [{}]".format(len(self._teams)))
