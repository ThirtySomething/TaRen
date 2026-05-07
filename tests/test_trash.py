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

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from taren.helper import Helper
from taren.trash import Trash


class TestTrash(unittest.TestCase):
    def test_init_creates_trash_folder_and_ignore_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            self.assertTrue(trash.init())
            self.assertTrue((Path(tmpdir) / ".trash").is_dir())
            self.assertTrue((Path(tmpdir) / ".trash" / ".ignore").exists())

    def test_init_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            self.assertTrue(trash.init())
            self.assertTrue(trash.init())

    def test_move_and_variant_naming(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            self.assertTrue(trash.init())

            src = Path(tmpdir) / "file.mp4"
            src.write_text("first", encoding="utf-8")
            trash.move(str(src))

            src.write_text("second", encoding="utf-8")
            trash.move(str(src))

            self.assertTrue((Path(tmpdir) / ".trash" / "file.mp4").exists())
            self.assertTrue((Path(tmpdir) / ".trash" / "file_1.mp4").exists())

    def test_move_returns_false_when_rename_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            self.assertTrue(trash.init())

            src = Path(tmpdir) / "file.mp4"
            src.write_text("first", encoding="utf-8")

            with patch("taren.trash.os.rename", side_effect=OSError("locked")):
                self.assertFalse(trash.move(str(src)))

    def test_cleanup_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            self.assertTrue(trash.init())
            trash_dir = Path(tmpdir) / ".trash"

            old_file = trash_dir / "old.mp4"
            old_file.write_text("x", encoding="utf-8")
            os.utime(old_file, (0, 0))

            new_file = trash_dir / "new.mp4"
            new_file.write_text("x", encoding="utf-8")

            deleted = trash.cleanup()
            self.assertEqual(deleted, 1)
            self.assertFalse(old_file.exists())
            self.assertTrue(new_file.exists())

            self.assertEqual(trash.list(), 1)

    def test_cleanup_deletes_ignore_file_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            self.assertTrue(trash.init())
            ignore_path = Path(tmpdir) / ".trash" / ".ignore"
            ignore_path.write_text("x", encoding="utf-8")

            with patch("taren.trash.Helper.delete_file", wraps=Helper.delete_file) as delete_mock:
                trash.cleanup()

            self.assertTrue(delete_mock.called)


if __name__ == "__main__":
    unittest.main()
