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

from taren.leadingnumbermatchrule import LeadingNumberMatchRule


class TestLeadingNumberMatchRule(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = LeadingNumberMatchRule()

    def test_leading_number_match_success(self) -> None:
        # When filename starts with valid episode ID
        episode = SimpleNamespace(episode_id=123)
        filename = "0123 Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)

    def test_leading_number_no_match_different_id(self) -> None:
        # When leading number doesn't match episode ID
        episode = SimpleNamespace(episode_id=123)
        filename = "0456 Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertFalse(result)

    def test_leading_number_no_number_in_filename(self) -> None:
        # When filename doesn't start with 4-digit number
        episode = SimpleNamespace(episode_id=123)
        filename = "Test 0123 Episode"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_leading_number_less_than_4_digits(self) -> None:
        # When leading number is less than 4 digits
        episode = SimpleNamespace(episode_id=123)
        filename = "123 Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_leading_number_without_space(self) -> None:
        # When leading number not followed by space
        episode = SimpleNamespace(episode_id=123)
        filename = "0123Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_leading_number_zero_id(self) -> None:
        # When episode ID is 0
        episode = SimpleNamespace(episode_id=0)
        filename = "0000 Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)

    def test_leading_number_large_id(self) -> None:
        # When episode ID is large
        episode = SimpleNamespace(episode_id=9999)
        filename = "9999 Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)
