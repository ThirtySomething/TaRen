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
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from taren.helper import Helper
from taren.tarendefines import FileSystemError
from taren.trash import Trash


class TestTrash(unittest.TestCase):
    def test_init_creates_trash_folder_and_ignore_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            trash.init()  # Should not raise
            self.assertTrue((Path(tmpdir) / ".trash").is_dir())
            self.assertTrue((Path(tmpdir) / ".trash" / ".ignore").exists())

    def test_init_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            trash.init()  # Should not raise
            trash.init()  # Should not raise

    def test_init_raises_on_directory_creation_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            with patch("taren.trash.Helper.ensure_directory", return_value=False):
                with self.assertRaises(FileSystemError):
                    trash.init()

    def test_move_and_variant_naming(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            trash.init()

            src = Path(tmpdir) / "file.mp4"
            src.write_text("first", encoding="utf-8")
            trash.move(str(src))

            src.write_text("second", encoding="utf-8")
            trash.move(str(src))

            self.assertTrue((Path(tmpdir) / ".trash" / "file_01.mp4").exists())
            self.assertTrue((Path(tmpdir) / ".trash" / "file_02.mp4").exists())

    def test_move_returns_false_when_rename_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            trash.init()

            src = Path(tmpdir) / "file.mp4"
            src.write_text("first", encoding="utf-8")

            with patch("taren.trash.os.rename", side_effect=OSError("locked")):
                self.assertFalse(trash.move(str(src)))

    def test_cleanup_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            trash.init()
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
            trash.init()
            ignore_path = Path(tmpdir) / ".trash" / ".ignore"
            ignore_path.write_text("x", encoding="utf-8")

            with patch("taren.trash.Helper.delete_file", wraps=Helper.delete_file) as delete_mock:
                trash.cleanup()

            self.assertTrue(delete_mock.called)

    def test_concurrent_move_produces_distinct_variant_names(self) -> None:
        """Two parallel move() calls must not overwrite each other's trash entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            trash.init()
            trash_dir = Path(tmpdir) / ".trash"

            src_a = Path(tmpdir) / "file.mp4"
            src_b = Path(tmpdir) / "file2.mp4"
            src_a.write_text("aaa", encoding="utf-8")
            src_b.write_text("bbb", encoding="utf-8")

            barrier = threading.Barrier(2)

            def move_a() -> None:
                barrier.wait()
                trash.move(str(src_a))

            def move_b() -> None:
                barrier.wait()
                trash.move(str(src_b))

            t1 = threading.Thread(target=move_a)
            t2 = threading.Thread(target=move_b)
            t1.start()
            t2.start()
            t1.join()
            t2.join()

            # Both files must end up in trash under distinct names
            trashed = [f.name for f in trash_dir.iterdir() if f.is_file() and f.name != ".ignore"]
            self.assertEqual(len(trashed), 2)
            self.assertEqual(len(set(trashed)), 2)

    def test_cleanup_respects_trash_retention_age_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trash = Trash(tmpdir, ".trash", 1, ".ignore")
            trash.init()
            trash_dir = Path(tmpdir) / ".trash"

            now = time.time()
            too_old = trash_dir / "too_old.mp4"
            too_old.write_text("x", encoding="utf-8")
            os.utime(too_old, (now - 3 * 86400, now - 3 * 86400))

            still_fresh = trash_dir / "still_fresh.mp4"
            still_fresh.write_text("x", encoding="utf-8")
            os.utime(still_fresh, (now - 12 * 3600, now - 12 * 3600))

            deleted = trash.cleanup()

            self.assertEqual(deleted, 1)
            self.assertFalse(too_old.exists())
            self.assertTrue(still_fresh.exists())


if __name__ == "__main__":
    unittest.main()
