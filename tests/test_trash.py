import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from taren.helper import Helper
from taren.trash import Trash


class TestTrash(unittest.TestCase):
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

            with patch(
                "taren.trash.Helper.delete_file", wraps=Helper.delete_file
            ) as delete_mock:
                trash.cleanup()

            self.assertTrue(delete_mock.called)


if __name__ == "__main__":
    unittest.main()
