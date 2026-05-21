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

logger = logging.getLogger(__name__)


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
        self.episode_broadcast_date: str = ""
        self.episode_cast: str = ""
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
        measstring: str = (
            f"Tatort - {self.episode_id:04d} - {self.episode_name} - {self.episode_inspectors} - {self.episode_sequence} - {self.episode_broadcast} - {self.episode_year}"
        )
        return measstring

    ############################################################################
    def _strip_invalid_characters(self) -> None:
        """
        Remove characters which are invalid for filenames
        """
        fields: tuple[tuple[str, str], ...] = (
            ("episode_broadcast", " "),
            ("episode_broadcast_date", " "),
            ("episode_cast", " "),
            ("episode_inspectors", " "),
            ("episode_name", " "),
            ("episode_sequence", "-"),
        )
        for field_name, replacement in fields:
            value: str = getattr(self, field_name)
            for current_invalid_character in Episode._invalid_characters:
                value = value.replace(current_invalid_character, replacement)
            setattr(self, field_name, value.strip())

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
    def _validate_row_structure(self, data_row: list[str]) -> bool:
        """Validate that the row contains the minimum required columns."""
        if len(data_row) < 6:
            logger.warning("skip malformed episode row (expected >= 6 columns): %s", data_row)
            return False
        return True

    ############################################################################
    def _extract_episode_id(self, data_row: list[str]) -> int | None:
        """Extract numeric episode id from first column."""
        episode_id_raw: Match[str] | None = re.search(r"([0-9]+)", data_row[0])
        if episode_id_raw is None:
            logger.warning("skip episode row without valid episode id: %s", data_row)
            return None
        return int(episode_id_raw.group(1))

    ############################################################################
    def _extract_episode_year(self, data_row: list[str]) -> int | None:
        """Extract 4-digit episode year from year column."""
        episode_year_raw: Match[str] | None = re.search(r"([0-9]{4})", data_row[3])
        if episode_year_raw is None:
            logger.warning("skip episode row without valid episode year: %s", data_row)
            return None
        return int(episode_year_raw.group(1))

    ############################################################################
    @staticmethod
    def _remove_parenthesized_text(text: str, pattern: str | None = None) -> str:
        """Remove text fragments enclosed in parentheses using a configurable pattern."""
        if pattern is None:
            pattern = r"\([^)]*\)"
        return re.sub(pattern, "", text).strip()

    ############################################################################
    def _extract_episode_name(self, data_row: list[str]) -> str:
        """Extract and normalize episode name."""
        return self._remove_parenthesized_text(data_row[1].strip(), r"\(Folge [0-9]+(.)+\)")

    ############################################################################
    def _extract_episode_inspectors(self, data_row: list[str]) -> str:
        """Extract and normalize inspector information."""
        return self._remove_parenthesized_text(data_row[4].strip(), r"\(Gastauftritt(.)+\)")

    ############################################################################
    def _extract_episode_sequence(self, data_row: list[str]) -> str:
        """Extract and normalize episode sequence value."""
        return self._remove_parenthesized_text(data_row[5].strip(), r"(\(\s*[0-9]*\)*)")

    ############################################################################
    def parse(self, data_row: list[str]) -> None:
        """
        Fill episode object with episode number, name and inspectors. Perform some cleanup on episode name and inspectors.
        """
        if not self._validate_row_structure(data_row):
            return

        episode_id = self._extract_episode_id(data_row)
        if episode_id is None:
            return

        episode_year = self._extract_episode_year(data_row)
        if episode_year is None:
            return

        self.episode_id = episode_id
        self.episode_year = episode_year
        self.episode_name = self._extract_episode_name(data_row)
        self.episode_inspectors = self._extract_episode_inspectors(data_row)
        self.episode_broadcast = data_row[2].strip()
        self.episode_sequence = self._extract_episode_sequence(data_row)

        if len(data_row) > 6:
            self.episode_broadcast_date = data_row[6].strip()
        if len(data_row) > 7:
            self.episode_cast = data_row[7].strip()

        self._strip_invalid_characters()
        self.empty = False
