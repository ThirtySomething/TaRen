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

from taren.episodenamecontainsrule import EpisodeNameContainsRule


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
        self.assertIsNone(result)

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
