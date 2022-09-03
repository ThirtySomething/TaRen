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
from typing import Match


class Episode:
    """
    Object with episode information. Retrieve data from given data row, do some
    cleanup and represents the default episode name in __repr__ method.
    """

    # Invalid characters inside filenames on Windows
    _invalid_characters: list[str] = ['"', "*", "<", ">", "?", "\\", "|", "/", ":"]

    ############################################################################
    def __init__(self: object) -> None:
        """
        Default is an empty episode for __repr__ method
        """
        self.empty: bool = True
        self.episode_broadcast: str = ""
        self.episode_id: int = 0
        self.episode_inspectors: str = ""
        self.episode_name: str = ""

    ############################################################################
    def __gt__(self: object, other: object) -> bool:
        """
        Used for sorting
        """
        if isinstance(other, Episode):
            return self.__repr__() > other.__repr__()
        raise Exception("Cannot compare Episode to Not-A-Episode")

    ############################################################################
    def __repr__(self: object) -> str:
        """
        Default string representation of an episode
        """
        measstring: str = "Tatort - {:04d} - {} - {} - {}".format(self.episode_id, self.episode_name, self.episode_inspectors, self.episode_broadcast)
        return measstring

    ############################################################################
    def _strip_invalid_characters(self: object) -> None:
        """
        Remove characters which are invalid for filenames
        """
        for current_invalid_character in Episode._invalid_characters:
            self.episode_broadcast = self.episode_broadcast.replace(current_invalid_character, " ").strip()
            self.episode_inspectors = self.episode_inspectors.replace(current_invalid_character, " ").strip()
            self.episode_name = self.episode_name.replace(current_invalid_character, " ").strip()

    ############################################################################
    def matches(self: object, filename: str) -> bool:
        """
        Check if episode matches the filename
        """
        # Check leading episode number => download marked as special episode manually
        filename_match: Match[str] = re.search(r"(^[0-9]{4} )", filename)
        if filename_match:
            filename_id: int = int(filename_match.group(1))
            return self.episode_id == filename_id

        # Check for download of dailymotion
        filename_match: Match[str] = re.search(r"(_E([0-9]{3,4})_)", filename)
        if filename_match:
            filename_id: int = int(filename_match.group(2))
            return self.episode_id == filename_id

        # Check episode prefix with number => alredy handled by TaRen
        filename_match: Match[str] = re.search(r"^(Tatort - ([0-9]{4}) )", filename)
        if filename_match:
            filename_id: int = int(filename_match.group(2))
            return self.episode_id == filename_id

        # Last check => Is episode name part of filename
        return self.episode_name.lower() in filename.lower()

    ############################################################################
    def parse(self: object, data_row: list[str]):
        """
        Fill episode object with episode number, name and inspectors. Perform some cleanup on episode name and inspectors.
        """
        if len(data_row) == 0:
            return
        logging.debug("data row {}".format(data_row))
        # Episode number is first element of row
        episode_id_raw: Match[str] = re.search(r"([0-9]+)", data_row[0])
        self.episode_id = int(episode_id_raw.group(1))
        # Episode name is second element of row, strip unwanted information like '(Folge 332 trägt den gleichen Titel)' using regexp
        self.episode_name = re.sub(r"\(Folge [0-9]+(.)+\)", "", data_row[1].strip()).strip()
        # Inspectors of episode, 5th element of row, strip unwanted information like '(Gastauftritt Trimmel und Kreutzer)' using regexp
        self.episode_inspectors = re.sub(r"\(Gastauftritt(.)+\)", "", data_row[4].strip()).strip()
        # Get name of broadcast station, 3rd element of row
        self.episode_broadcast = data_row[2].strip()
        # Strip invalid characters
        self._strip_invalid_characters()
        # Mark as not empty
        self.empty = False
