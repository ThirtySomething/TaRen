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

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from taren.helper import Helper


class TestHelper(unittest.TestCase):
    def test_ensure_directory_creates_folder(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "new-folder"
            self.assertFalse(target.exists())
            self.assertTrue(Helper.ensure_directory(str(target)))
            self.assertTrue(target.exists())

    def test_delete_file_returns_expected_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing.txt"
            self.assertFalse(Helper.delete_file(str(missing)))

            existing = Path(tmpdir) / "exists.txt"
            existing.write_text("hello", encoding="utf-8")
            self.assertTrue(Helper.delete_file(str(existing)))
            self.assertFalse(existing.exists())

    def test_ensure_directory_failure_and_wrapper(self) -> None:
        with (
            patch("taren.helper.os.path.exists", return_value=False),
            patch("taren.helper.os.makedirs", side_effect=OSError),
        ):
            self.assertFalse(Helper.ensure_directory("/not/creatable"))

        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "wrapper-folder"
            self.assertTrue(Helper.ensure_directory(str(target)))

    def test_delete_file_oserror_branch(self) -> None:
        with (
            patch("taren.helper.os.path.exists", return_value=True),
            patch("taren.helper.os.remove", side_effect=OSError),
        ):
            self.assertFalse(Helper.delete_file("/cannot/delete"))


if __name__ == "__main__":
    unittest.main()
