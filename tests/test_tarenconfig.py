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
from pathlib import Path
import tempfile
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

    def test_validate_accepts_valid_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            collection_dir = str(Path(tmpdir) / "collection")
            Path(collection_dir).mkdir()
            config = TarenConfig("dummy.json", auto_load=False)
            config.value_set("taren", "collection", collection_dir)
            config.value_set("taren", "wiki", "https://example.invalid/wiki")
            config.value_set("taren", "maxcache", "1")
            config.value_set("taren", "trashage", "0")
            config.value_set("taren", "http_timeout", "10")
            config.value_set("taren", "http_retries", "2")
            config.value_set("logging", "loglevel", "info")
            config.value_set("logging", "logfile", "TaRen.log")

            self.assertEqual(config.validate(), [])

    def test_validate_rejects_invalid_numeric_url_and_path_values(self) -> None:
        config = TarenConfig("dummy.json", auto_load=False)
        config.value_set("taren", "collection", "/path/does/not/exist")
        config.value_set("taren", "wiki", "invalid-url")
        config.value_set("taren", "maxcache", "not-a-number")
        config.value_set("taren", "trashage", "-1")
        config.value_set("taren", "http_timeout", "0")
        config.value_set("taren", "http_retries", "0")

        errors = config.validate()

        self.assertTrue(any("taren.collection" in error for error in errors))
        self.assertTrue(any("taren.wiki" in error for error in errors))
        self.assertTrue(any("taren.maxcache" in error for error in errors))
        self.assertTrue(any("taren.trashage" in error for error in errors))
        self.assertTrue(any("taren.http_timeout" in error for error in errors))
        self.assertTrue(any("taren.http_retries" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
