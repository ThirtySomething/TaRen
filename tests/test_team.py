import unittest

from taren.episode import Episode
from taren.team import Team


class TestTeam(unittest.TestCase):
    def test_gt_returns_not_implemented_for_other_type(self) -> None:
        team = Team()
        self.assertIs(team.__gt__("x"), NotImplemented)

    def test_repr_branches(self) -> None:
        team = Team()
        team.team_location = "Berlin"
        team.team_inspectors = ["Max"]
        team.team_episode_count = 1

        team.team_ended = False
        team.team_period_begin = 2010
        self.assertIn("seit 2010", repr(team))

        team.team_ended = True
        team.team_period_begin = 2011
        team.team_period_end = 2011
        self.assertIn("2011", repr(team))

        team.team_period_end = 2014
        self.assertIn("2011-2014", repr(team))

    def test_parse_skips_short_or_invalid_rows(self) -> None:
        team = Team()
        team.parse(["x"])
        self.assertTrue(team.empty)

        team.parse(["invalid", "A", "B", "C", "D", "1"])
        self.assertTrue(team.empty)

        team.parse(["seit 2010", "A", "B", "C", "D", "invalid"])
        self.assertTrue(team.empty)

    def test_parse_populates_valid_row(self) -> None:
        team = Team()
        team.parse(["seit 2010", "Max Mustermann", "x", "x", "Berlin", "10"])
        self.assertFalse(team.empty)
        self.assertEqual(team.team_period_begin, 2010)
        self.assertGreaterEqual(team.team_period_end, 2010)
        self.assertEqual(team.team_location, "Berlin")
        self.assertEqual(team.team_episode_count, 10)

    def test_matches_checks_period_and_inspectors(self) -> None:
        team = Team()
        team.parse(["2010-2012", "Max", "x", "x", "Berlin", "3"])

        ep = Episode()
        ep.empty = False
        ep.episode_year = 2011
        ep.episode_inspectors = "Max"
        self.assertTrue(team.matches(ep))

        ep.episode_year = 2009
        self.assertFalse(team.matches(ep))


if __name__ == "__main__":
    unittest.main()
