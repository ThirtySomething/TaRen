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
from types import NotImplementedType
from typing import Match

from taren.dailymotiontokenmatchrule import DailymotionTokenMatchRule
from taren.episodematchrule import EpisodeMatchRule
from taren.episodenamecontainsrule import EpisodeNameContainsRule
from taren.exactrepresentationmatchrule import ExactRepresentationMatchRule
from taren.leadingnumbermatchrule import LeadingNumberMatchRule
from taren.tatortprefixmatchrule import TatortPrefixMatchRule


class Episode:
    """
    Object with episode information. Retrieve data from given data row, do some
    cleanup and represents the default episode name in __repr__ method.
    """

    # Invalid characters inside filenames on Windows
    _invalid_characters: list[str] = ['"', "*", "<", ">", "?", "\\", "|", "/", ":"]
    _match_rules: tuple[EpisodeMatchRule, ...] = (
        ExactRepresentationMatchRule(),
        LeadingNumberMatchRule(),
        DailymotionTokenMatchRule(),
        TatortPrefixMatchRule(),
        EpisodeNameContainsRule(),
    )

    ############################################################################
    def __init__(self) -> None:
        """
        Default is an empty episode for __repr__ method
        """
        self.empty: bool = True
        self.episode_broadcast: str = ""
        self.episode_id: int = 0
        self.episode_inspectors: str = ""
        self.episode_name: str = ""
        self.episode_sequence: str = ""
        self.episode_url: str = ""
        self.episode_year: int = 0

    ############################################################################
    @classmethod
    def empty_instance(cls) -> "Episode":
        """Return an explicit empty episode null-object instance."""
        return cls()

    ############################################################################
    def __gt__(self, other: object) -> bool | NotImplementedType:
        """
        Used for sorting
        """
        if not isinstance(other, Episode):
            return NotImplemented
        return self.__repr__() > other.__repr__()

    ############################################################################
    def __repr__(self) -> str:
        """
        Default string representation of an episode
        """
        measstring: str = "Tatort - {:04d} - {} - {} - {} - {} - {}".format(
            self.episode_id,
            self.episode_name,
            self.episode_inspectors,
            self.episode_sequence,
            self.episode_broadcast,
            self.episode_year,
        )
        return measstring

    ############################################################################
    def _strip_invalid_characters(self) -> None:
        """
        Remove characters which are invalid for filenames
        """
        for current_invalid_character in Episode._invalid_characters:
            self.episode_broadcast = self.episode_broadcast.replace(current_invalid_character, " ").strip()
            self.episode_inspectors = self.episode_inspectors.replace(current_invalid_character, " ").strip()
            self.episode_name = self.episode_name.replace(current_invalid_character, " ").strip()
            self.episode_sequence = self.episode_sequence.replace(current_invalid_character, "-").strip()

    ############################################################################
    def matches(self, filename: str) -> bool:
        """
        Check if episode matches the filename
        """
        for rule in self._match_rules:
            match_result = rule.try_match(filename, self)
            if match_result is not None:
                return match_result
        return False

    ############################################################################
    def parse(self, data_row: list[str]) -> None:
        """
        Fill episode object with episode number, name and inspectors. Perform some cleanup on episode name and inspectors.
        """
        if len(data_row) < 6:
            logging.warning("skip malformed episode row (expected >= 6 columns): %s", data_row)
            return
        # Episode number is first element of row
        episode_id_raw: Match[str] | None = re.search(r"([0-9]+)", data_row[0])
        if episode_id_raw is None:
            logging.warning("skip episode row without valid episode id: %s", data_row)
            return
        self.episode_id = int(episode_id_raw.group(1))
        # Year of episode
        episode_year_raw: Match[str] | None = re.search(r"([0-9]{4})", data_row[3])
        if episode_year_raw is None:
            logging.warning("skip episode row without valid episode year: %s", data_row)
            return
        self.episode_year = int(episode_year_raw.group(1))
        # Episode name is second element of row, strip unwanted information like '(Folge 332 trägt den gleichen Titel)' using regexp
        self.episode_name = re.sub(r"\(Folge [0-9]+(.)+\)", "", data_row[1].strip()).strip()
        # Inspectors of episode, 5th element of row, strip unwanted information like '(Gastauftritt Trimmel und Kreutzer)' using regexp
        self.episode_inspectors = re.sub(r"\(Gastauftritt(.)+\)", "", data_row[4].strip()).strip()
        # Get name of broadcast station, 3rd element of row
        self.episode_broadcast = data_row[2].strip()
        # Get sequence number and strip alternative numbering.
        self.episode_sequence = re.sub(r"(\(\s*[0-9]*\)*)", "", data_row[5].strip()).strip()
        # Strip invalid characters
        self._strip_invalid_characters()
        # Mark as not empty
        self.empty = False
