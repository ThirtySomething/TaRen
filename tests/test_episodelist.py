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
from unittest.mock import patch

from fakeepisodesource import FakeEpisodeSource
from taren.cachedhtmlepisodesource import CachedHtmlEpisodeSource
from taren.episodelist import EpisodeList
from taren.episode import Episode


class TestEpisodeList(unittest.TestCase):
    def test_parse_website_guards(self) -> None:
        el = EpisodeList("Tatort", "http://example", 1, "ua")
        self.assertEqual(el._parse_website(""), [])
        self.assertEqual(el._parse_website("<html><body>No table</body></html>"), [])

    def test_build_skips_short_rows(self) -> None:
        html = """
        <table>
            <tr><th>header</th></tr>
            <tr><td>123</td><td>Name</td><td>ARD</td><td>2020</td><td>Inspector</td><td>1</td></tr>
        </table>
        """
        el = EpisodeList("Tatort", "http://example", 1, "ua")
        episodes = el._parse_website(html)
        self.assertEqual(len(episodes), 1)

    def test_parse_skips_malformed_data_rows_but_keeps_valid_ones(self) -> None:
        html = """
        <table>
            <tr><td>abc</td><td>BadId</td><td>ARD</td><td>2020</td><td>Inspector</td><td>1</td></tr>
            <tr><td>124</td><td>Good</td><td>ARD</td><td>2021</td><td>Inspector</td><td>2</td></tr>
        </table>
        """
        el = EpisodeList("Tatort", "http://example", 1, "ua")
        episodes = el._parse_website(html)
        self.assertEqual(len(episodes), 1)
        self.assertEqual(episodes[0].episode_id, 124)

    def test_getters_and_find(self) -> None:
        html = """
        <table>
            <tr><td>123</td><td>Fall A</td><td>ARD</td><td>2020</td><td>Inspector</td><td>1</td></tr>
        </table>
        """
        source = FakeEpisodeSource(html)
        el = EpisodeList("Tatort", "http://example", 1, "ua", episode_source=source)
        el.get_episodes()

        self.assertEqual(el.get_episode_count(), 1)
        self.assertEqual(source.called, 1)
        found = el.find_episode("Fall A in filename")
        self.assertFalse(found.empty)
        self.assertTrue(el.find_episode("completely unrelated").empty)

    def test_cached_html_episode_source_uses_website_cache(self) -> None:
        with patch("taren.cachedhtmlepisodesource.WebSiteCache") as cache_cls:
            cache_instance = cache_cls.return_value
            cache_instance.get_website_from_cache.return_value = "<html></html>"
            source = CachedHtmlEpisodeSource("Tatort", "http://example", 1, "ua")

            payload = source.fetch()

            cache_cls.assert_called_once_with(
                "Tatort",
                "http://example",
                1,
                "ua",
                fetch_policy=None,
                cache_dir=None,
            )
            cache_instance.get_website_from_cache.assert_called_once_with()
            self.assertEqual(payload, "<html></html>")

    def test_cached_html_episode_source_passes_custom_fetch_policy(self) -> None:
        with patch("taren.cachedhtmlepisodesource.WebSiteCache") as cache_cls:
            policy = object()
            CachedHtmlEpisodeSource("Tatort", "http://example", 1, "ua", fetch_policy=policy)

            cache_cls.assert_called_once_with(
                "Tatort",
                "http://example",
                1,
                "ua",
                fetch_policy=policy,
                cache_dir=None,
            )

    def test_find_episode_uses_empty_instance_factory(self) -> None:
        el = EpisodeList("Tatort", "http://example", 1, "ua")
        with patch.object(Episode, "empty_instance", wraps=Episode.empty_instance) as factory:
            missing = el.find_episode("no hit")

        factory.assert_called_once_with()
        self.assertTrue(missing.empty)


if __name__ == "__main__":
    unittest.main()
