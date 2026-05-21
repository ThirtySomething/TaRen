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

from taren.dailymotiontokenmatchrule import DailymotionTokenMatchRule


class TestDailymotionTokenMatchRule(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = DailymotionTokenMatchRule()

    def test_dailymotion_token_3_digit_match(self) -> None:
        # When filename contains _E123_ token with 3 digits
        episode = SimpleNamespace(episode_id=123)
        filename = "Show_Name_E123_Part.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)

    def test_dailymotion_token_4_digit_match(self) -> None:
        # When filename contains _E1234_ token with 4 digits
        episode = SimpleNamespace(episode_id=1234)
        filename = "Show_Name_E1234_Part.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)

    def test_dailymotion_token_no_match_wrong_id(self) -> None:
        # When token ID doesn't match episode ID
        episode = SimpleNamespace(episode_id=123)
        filename = "Show_Name_E456_Part.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertFalse(result)

    def test_dailymotion_token_not_present(self) -> None:
        # When filename has no _EXXX_ token
        episode = SimpleNamespace(episode_id=123)
        filename = "Show_Name_123_Part.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_dailymotion_token_only_2_digits(self) -> None:
        # When _EXXX_ has only 2 digits (too short)
        episode = SimpleNamespace(episode_id=12)
        filename = "Show_Name_E12_Part.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_dailymotion_token_5_digits(self) -> None:
        # When _EXXX_ has 5 digits (too long)
        episode = SimpleNamespace(episode_id=12345)
        filename = "Show_Name_E12345_Part.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_dailymotion_token_zero_id(self) -> None:
        # When episode ID is 000
        episode = SimpleNamespace(episode_id=0)
        filename = "Show_Name_E000_Part.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)
