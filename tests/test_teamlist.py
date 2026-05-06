import unittest
from unittest.mock import patch

from taren.episode import Episode
from taren.teamlist import TeamList


class TestTeamList(unittest.TestCase):
    def test_parse_website_guards(self) -> None:
        tl = TeamList("Teams", "http://example", 1, "ua")
        self.assertEqual(tl._parse_website(""), [])
        self.assertEqual(tl._parse_website("<html><body>No table</body></html>"), [])

    def test_build_skips_short_rows(self) -> None:
        html = """
        <table>
            <tr><th>header</th></tr>
            <tr><td>seit 2010</td><td>Max</td><td>X</td><td>Y</td><td>Berlin</td><td>3</td></tr>
        </table>
        """
        tl = TeamList("Teams", "http://example", 1, "ua")
        teams = tl._parse_website(html)
        self.assertEqual(len(teams), 1)

    def test_getters_and_find(self) -> None:
        html = """
        <table>
            <tr><td>seit 2010</td><td>Max</td><td>X</td><td>Y</td><td>Berlin</td><td>3</td></tr>
        </table>
        """
        tl = TeamList("Teams", "http://example", 1, "ua")
        with patch.object(TeamList, "_read_website", return_value=html):
            tl.get_teams()

        self.assertEqual(tl.get_team_count(), 1)
        episode = Episode()
        episode.empty = False
        episode.episode_year = 2015
        episode.episode_inspectors = "Max"
        self.assertFalse(tl.find_team(episode).empty)

        episode.episode_inspectors = "Other"
        self.assertTrue(tl.find_team(episode).empty)


if __name__ == "__main__":
    unittest.main()
