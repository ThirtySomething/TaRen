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
import re
from datetime import date
from typing import Match

from taren.episode import Episode


class Team:
    """
    Object with team information. Retrieve data from given data row, do some
    cleanup and represents the default team name in __repr__ method.
    """

    # Invalid characters inside filenames on Windows
    _invalid_characters: list[str] = ['"', "*", "<", ">", "?", "\\", "|", "/", ":"]

    ############################################################################
    def __init__(self: object) -> None:
        """
        Default is an empty team for __repr__ method
        """
        self.empty: bool = True
        self.team_period_begin: int = 0
        self.team_period_end: int = 0
        self.team_inspectors: list[str] = []
        self.team_location: str = ""
        self.team_episode_count: int = 0
        self.team_ended: bool = False

    ############################################################################
    def __gt__(self: object, other: object) -> bool:
        """
        Used for sorting
        """
        if isinstance(other, Team):
            return self.__repr__() > other.__repr__()
        raise Exception("Cannot compare Team to Not-A-Team")

    ############################################################################
    def __repr__(self: object) -> str:
        """
        Default string representation of an episode
        """
        period: str = ""
        if self.team_ended:
            if self.team_period_begin == self.team_period_end:
                period = "{}".format(self.team_period_begin)
            else:
                period = "{}-{}".format(self.team_period_begin, self.team_period_end)
        else:
            period = "seit {}".format(self.team_period_begin)

        measstring: str = "{} - {} ({}), {}".format(self.team_location, self.team_inspectors[0], self.team_episode_count, period)
        return measstring

    ############################################################################
    def _strip_invalid_characters(self: object) -> None:
        """
        Remove characters which are invalid for filenames
        """
        for current_invalid_character in Team._invalid_characters:
            self.team_location = self.team_location.replace(current_invalid_character, " ").strip()
            for index, inspector in self.team_inspectors:
                self.team_inspectors[index] = inspector.replace(current_invalid_character, " ").strip()

    ############################################################################
    def matches(self: object, episode: Episode) -> bool:
        """
        Check if episode matches the team
        """
        if not self.team_period_begin <= episode.episode_year:
            # Abort - episode is older than team
            return False

        if not self.team_period_end >= episode.episode_year:
            # Abort - episode is younger than team
            return False

        # Check for at least one inspector of team is in episode
        inspectorMatch: int = 0
        inspectorCheck: str = episode.episode_inspectors.lower()
        for inspector in self.team_inspectors:
            if not -1 == inspectorCheck.find(inspector.lower()):
                inspectorMatch = inspectorMatch + 1

        return len(self.team_inspectors) == inspectorMatch

    ############################################################################
    def parse(self: object, data_row: list[str]):
        """
        Fill episode object with episode number, name and inspectors. Perform some cleanup on episode name and inspectors.
        """
        if len(data_row) == 0:
            return
        # logging.debug("data row {}".format(data_row))

        # Fiddle out team period and running flag
        team_period_raw: Match[str] = re.search(r"(seit )?([0-9]{4})((.*)([0-9]{4}))?", data_row[0])
        # logging.debug("team_period_raw.groups() {}".format(team_period_raw.groups()))
        if None == team_period_raw.group(1):
            self.team_ended = True
        else:
            self.team_ended = False
        self.team_period_begin: int = int(team_period_raw.group(2))
        # Handle running period
        if not None == team_period_raw.group(1) and None == team_period_raw.group(3) and None == team_period_raw.group(4) and None == team_period_raw.group(5):
            self.team_period_end: int = int(date.today().year)
        # Handle single year
        if None == team_period_raw.group(1) and None == team_period_raw.group(3) and None == team_period_raw.group(4) and None == team_period_raw.group(5):
            self.team_period_end: int = self.team_period_begin
        # Handle time period
        if None == team_period_raw.group(1) and not None == team_period_raw.group(3) and not None == team_period_raw.group(4) and not None == team_period_raw.group(5):
            self.team_period_end: int = int(team_period_raw.group(5))

        # Create list of inspectors
        # Split names by comma
        for cur_inspector in data_row[1].split(","):
            # Strip everything inside round brackets
            inspector_raw: Match[str] = re.sub(r"\([^\)]+\)", "", cur_inspector.strip()).strip()
            # Split by space and get last element (this is the name of the inspector)
            inspector: str = inspector_raw.split(" ")[-1]
            # Append inspector to list
            self.team_inspectors.append(inspector)

        # Fiddle out location(s)
        locations: list[str] = []
        # Split locations by comma
        for cur_location in data_row[4].split(","):
            # Strip everything inside round brackets
            location_raw: Match[str] = re.sub(r"\([^\)]+\)", "", cur_location.strip()).strip()
            # Append location to list
            locations.append(location_raw.strip())
        # Set location string
        self.team_location = ", ".join(locations)

        # Fiddle out number of episodes
        team_episode_count_raw: Match[str] = re.search(r"([0-9]+)", data_row[5])
        self.team_episode_count: int = int(team_episode_count_raw.group(1))

        # logging.debug("{}".format(self))
        # logging.debug("{}".format("-" * 80))

        # Mark as not empty
        self.empty = False
