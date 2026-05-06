import unittest
from unittest.mock import patch

from taren.episode import Episode


class TestEpisode(unittest.TestCase):
    def test_matches_stops_on_first_decisive_rule(self) -> None:
        class _NoneRule:
            def __init__(self) -> None:
                self.called = 0

            def try_match(self, filename: str, episode: Episode) -> bool | None:
                self.called += 1
                return None

        class _TrueRule:
            def __init__(self) -> None:
                self.called = 0

            def try_match(self, filename: str, episode: Episode) -> bool | None:
                self.called += 1
                return True

        class _FailRule:
            def try_match(self, filename: str, episode: Episode) -> bool | None:
                raise AssertionError("rule chain did not short-circuit")

        none_rule = _NoneRule()
        true_rule = _TrueRule()

        with patch.object(Episode, "_match_rules", (none_rule, true_rule, _FailRule())):
            self.assertTrue(Episode().matches("anything"))

        self.assertEqual(none_rule.called, 1)
        self.assertEqual(true_rule.called, 1)

    def test_empty_instance_factory_returns_empty_episode(self) -> None:
        episode = Episode.empty_instance()
        self.assertTrue(episode.empty)
        self.assertEqual(episode.episode_id, 0)

    def test_gt_returns_not_implemented_for_other_type(self) -> None:
        episode = Episode()
        self.assertIs(episode.__gt__("x"), NotImplemented)

    def test_gt_true_branch(self) -> None:
        a = Episode()
        b = Episode()
        a.episode_id = 2
        b.episode_id = 1
        self.assertTrue(a.__gt__(b))

    def test_parse_skips_short_and_invalid_rows(self) -> None:
        episode = Episode()
        episode.parse(["1"])
        self.assertTrue(episode.empty)

        episode.parse(["abc", "name", "station", "2020", "inspector", "1"])
        self.assertTrue(episode.empty)

        episode.parse(["123", "name", "station", "year", "inspector", "1"])
        self.assertTrue(episode.empty)

    def test_parse_populates_valid_row(self) -> None:
        episode = Episode()
        episode.parse(["123", "Folge", "ARD", "2020", "Inspector", "1"])
        self.assertFalse(episode.empty)
        self.assertEqual(episode.episode_id, 123)
        self.assertEqual(episode.episode_year, 2020)
        self.assertEqual(episode.episode_sequence, "1")

    def test_matches_uses_multiple_patterns(self) -> None:
        episode = Episode()
        episode.episode_id = 123
        episode.episode_name = "Mein Fall"
        episode.episode_inspectors = "Inspector"
        episode.episode_broadcast = "ARD"
        episode.episode_sequence = "1"
        episode.episode_year = 2020

        self.assertTrue(episode.matches(str(episode)))
        self.assertTrue(episode.matches("0123 special episode"))
        self.assertTrue(episode.matches("foo_E0123_bar"))
        self.assertTrue(episode.matches("Tatort - 0123 Something"))
        self.assertTrue(episode.matches("my meIN faLL sample"))
        self.assertFalse(episode.matches("unrelated"))


if __name__ == "__main__":
    unittest.main()
