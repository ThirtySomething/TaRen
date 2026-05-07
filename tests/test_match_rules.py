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

from fakeepisode import FakeEpisode
from taren.dailymotiontokenmatchrule import DailymotionTokenMatchRule
from taren.episode import Episode
from taren.episodenamecontainsrule import EpisodeNameContainsRule
from taren.exactrepresentationmatchrule import ExactRepresentationMatchRule
from taren.leadingnumbermatchrule import LeadingNumberMatchRule
from taren.tatortprefixmatchrule import TatortPrefixMatchRule


class TestExactRepresentationMatchRule(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = ExactRepresentationMatchRule()

    def test_exact_match_success(self) -> None:
        # When episode string representation matches filename exactly
        episode = FakeEpisode("Test Episode")
        filename = "Test Episode"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)

    def test_exact_match_failure_different_case(self) -> None:
        # When case differs, should not match
        episode = FakeEpisode("Test Episode")
        filename = "test episode"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_exact_match_failure_partial(self) -> None:
        # When only partial match, should not match
        episode = FakeEpisode("Test Episode")
        filename = "Test"
        result = self.rule.try_match(filename, episode)
        self.assertIsNone(result)

    def test_exact_match_empty_strings(self) -> None:
        # When both are empty
        episode = FakeEpisode("")
        filename = ""
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)

    def test_exact_match_with_special_characters(self) -> None:
        # When episode name has special characters
        episode = FakeEpisode("Test - Episode (2023)")
        filename = "Test - Episode (2023)"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)


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


class TestEpisodeNameContainsRule(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = EpisodeNameContainsRule()

    def test_name_contains_exact_match(self) -> None:
        # When episode name is contained in filename
        episode = SimpleNamespace(episode_name="The Investigation")
        filename = "The Investigation Complete.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)

    def test_name_contains_case_insensitive(self) -> None:
        # When match is case-insensitive
        episode = SimpleNamespace(episode_name="The Investigation")
        filename = "the investigation complete.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)

    def test_name_contains_mixed_case(self) -> None:
        # When mixed case in filename and episode name
        episode = SimpleNamespace(episode_name="The Investigation")
        filename = "The INVESTIGATION Complete.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)

    def test_name_contains_no_match(self) -> None:
        # When episode name not in filename
        episode = SimpleNamespace(episode_name="The Investigation")
        filename = "Other Show.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertFalse(result)

    def test_name_contains_partial_no_match(self) -> None:
        # When only partial episode name in filename
        episode = SimpleNamespace(episode_name="The Investigation")
        filename = "The Other Show.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertFalse(result)

    def test_name_contains_empty_episode_name(self) -> None:
        # When episode name is empty
        episode = SimpleNamespace(episode_name="")
        filename = "Any Filename.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)  # Empty string is contained in any string

    def test_name_contains_empty_filename(self) -> None:
        # When filename is empty
        episode = SimpleNamespace(episode_name="The Investigation")
        filename = ""
        result = self.rule.try_match(filename, episode)
        self.assertFalse(result)

    def test_name_contains_special_characters(self) -> None:
        # When episode name has special characters
        episode = SimpleNamespace(episode_name="The (Investigation)")
        filename = "The (Investigation) Complete.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)

    def test_name_contains_with_path(self) -> None:
        # When filename includes path
        episode = SimpleNamespace(episode_name="The Investigation")
        filename = "/path/to/the investigation complete.mp4"
        result = self.rule.try_match(filename, episode)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
