import unittest

from taren.stats import Stats


class TestStats(unittest.TestCase):
    def test_str_handles_zero_and_nonzero(self) -> None:
        stats = Stats()
        text = str(stats)
        self.assertIn("0.00%", text)

        stats.episodes_total = 10
        stats.episodes_owned = 5
        text = str(stats)
        self.assertIn("50.00%", text)


if __name__ == "__main__":
    unittest.main()
