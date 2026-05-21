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

import unittest
from types import SimpleNamespace

from taren.tatortprefixmatchrule import TatortPrefixMatchRule


class TestTatortPrefixMatchRule(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = TatortPrefixMatchRule()

    def test_tatort_prefix_match_success(self) -> None:
        # When filename starts with Tatort - YYYY format
        episode = SimpleNamespace(episode_id=2023)
        filename = "Tatort - 2023 Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)

    def test_tatort_prefix_no_match_wrong_year(self) -> None:
        # When Tatort year doesn't match episode ID
        episode = SimpleNamespace(episode_id=2023)
        filename = "Tatort - 2022 Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertFalse(result)

    def test_tatort_prefix_not_at_start(self) -> None:
        # When Tatort pattern not at filename start
        episode = SimpleNamespace(episode_id=2023)
        filename = "Test Tatort - 2023 Episode"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_tatort_prefix_wrong_format(self) -> None:
        # When format is wrong (missing dash or space)
        episode = SimpleNamespace(episode_id=2023)
        filename = "Tatort-2023 Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_tatort_prefix_no_space_after_year(self) -> None:
        # When no space after year
        episode = SimpleNamespace(episode_id=2023)
        filename = "Tatort - 2023Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_tatort_prefix_less_than_4_digits(self) -> None:
        # When year is less than 4 digits
        episode = SimpleNamespace(episode_id=202)
        filename = "Tatort - 202 Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_tatort_prefix_year_zero(self) -> None:
        # When year is 0000
        episode = SimpleNamespace(episode_id=0)
        filename = "Tatort - 0000 Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)
