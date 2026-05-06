import unittest
from unittest.mock import patch

from taren.episodelist import CachedHtmlEpisodeSource, EpisodeList
from taren.episode import Episode


class TestEpisodeList(unittest.TestCase):
    class _FakeEpisodeSource:
        def __init__(self, payload: str) -> None:
            self.payload = payload
            self.called = 0

        def fetch(self) -> str:
            self.called += 1
            return self.payload

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
        source = self._FakeEpisodeSource(html)
        el = EpisodeList("Tatort", "http://example", 1, "ua", episode_source=source)
        el.get_episodes()

        self.assertEqual(el.get_episode_count(), 1)
        self.assertEqual(source.called, 1)
        found = el.find_episode("Fall A in filename")
        self.assertFalse(found.empty)
        self.assertTrue(el.find_episode("completely unrelated").empty)

    def test_cached_html_episode_source_uses_website_cache(self) -> None:
        with patch("taren.episodelist.WebSiteCache") as cache_cls:
            cache_instance = cache_cls.return_value
            cache_instance.get_website_from_cache.return_value = "<html></html>"
            source = CachedHtmlEpisodeSource("Tatort", "http://example", 1, "ua")

            payload = source.fetch()

            cache_cls.assert_called_once_with("Tatort", "http://example", 1, "ua", fetch_policy=None)
            cache_instance.get_website_from_cache.assert_called_once_with()
            self.assertEqual(payload, "<html></html>")

    def test_cached_html_episode_source_passes_custom_fetch_policy(self) -> None:
        with patch("taren.episodelist.WebSiteCache") as cache_cls:
            policy = object()
            CachedHtmlEpisodeSource("Tatort", "http://example", 1, "ua", fetch_policy=policy)

            cache_cls.assert_called_once_with("Tatort", "http://example", 1, "ua", fetch_policy=policy)

    def test_find_episode_uses_empty_instance_factory(self) -> None:
        el = EpisodeList("Tatort", "http://example", 1, "ua")
        with patch.object(Episode, "empty_instance", wraps=Episode.empty_instance) as factory:
            missing = el.find_episode("no hit")

        factory.assert_called_once_with()
        self.assertTrue(missing.empty)


if __name__ == "__main__":
    unittest.main()
