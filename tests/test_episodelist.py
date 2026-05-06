import unittest
from unittest.mock import patch

from taren.episodelist import EpisodeList


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
        el = EpisodeList("Tatort", "http://example", 1, "ua")
        with patch.object(EpisodeList, "_read_website", return_value=html):
            el.get_episodes()

        self.assertEqual(el.get_episode_count(), 1)
        found = el.find_episode("Fall A in filename")
        self.assertFalse(found.empty)
        self.assertTrue(el.find_episode("completely unrelated").empty)


if __name__ == "__main__":
    unittest.main()
