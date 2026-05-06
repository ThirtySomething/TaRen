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
from typing import Any, cast

from taren.tarenconfig import TarenConfig


class TestTarenConfig(unittest.TestCase):
    def test_setup_returns_true_and_registers_expected_keys(self) -> None:
        calls: list[tuple[str, str, str]] = []

        class Dummy:
            def add(self, section: str, key: str, value: str) -> None:
                calls.append((section, key, value))

        self.assertTrue(TarenConfig.setup(cast(Any, Dummy())))
        self.assertTrue(
            any(section == "taren" and key == "wiki" for section, key, _ in calls)
        )
        self.assertTrue(
            any(section == "logging" and key == "logfile" for section, key, _ in calls)
        )


if __name__ == "__main__":
    unittest.main()
