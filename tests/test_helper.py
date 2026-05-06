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
            self.assertTrue(Helper.ensureDirectory(str(target)))

    def test_delete_file_oserror_branch(self) -> None:
        with (
            patch("taren.helper.os.path.exists", return_value=True),
            patch("taren.helper.os.remove", side_effect=OSError),
        ):
            self.assertFalse(Helper.delete_file("/cannot/delete"))


if __name__ == "__main__":
    unittest.main()
