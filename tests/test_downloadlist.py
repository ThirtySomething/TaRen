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

from taren.downloadlist import DownloadList


class TestDownloadList(unittest.TestCase):
    def test_get_filenames_filters_and_sorts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "Tatort_B.mp4").write_text("x", encoding="utf-8")
            Path(tmpdir, "Tatort_A.mp4").write_text("x", encoding="utf-8")
            Path(tmpdir, "Other.mp4").write_text("x", encoding="utf-8")

            self.assertEqual(DownloadList.get_filenames(tmpdir, "Tatort", ".mp4"), ["Tatort_A.mp4", "Tatort_B.mp4"])


if __name__ == "__main__":
    unittest.main()
