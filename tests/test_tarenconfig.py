import unittest
from typing import Any, cast

from taren.tarenconfig import TarenConfig


class TestTarenConfig(unittest.TestCase):
    def test_setup_returns_true_and_registers_expected_keys(self) -> None:
        calls: list[tuple[str, str, str]] = []

        class Dummy:
            def add(self, section: str, key: str, value: str) -> None:
                calls.append((section, key, value))

        self.assertTrue(TarenConfig.setup(cast(Any, Dummy())))
        self.assertTrue(any(section == "taren" and key == "wiki" for section, key, _ in calls))
        self.assertTrue(any(section == "logging" and key == "logfile" for section, key, _ in calls))


if __name__ == "__main__":
    unittest.main()
