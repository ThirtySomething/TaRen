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
from unittest.mock import MagicMock, patch

from taren.sizebasedconflictstrategy import SizeBasedConflictStrategy


class TestSizeBasedConflictStrategy(unittest.TestCase):
    def setUp(self) -> None:
        self.strategy = SizeBasedConflictStrategy()

    def test_no_conflict_when_new_file_missing(self) -> None:
        # When new file doesn't exist, no conflict
        result = self.strategy.resolve("/path/to/old.mp4", "/path/to/new.mp4")
        self.assertIsNone(result.move_to_trash)
        self.assertFalse(result.skip_rename)

    def test_conflict_when_old_and_new_equal_size(self) -> None:
        # When files are same size, trash the source file (download) and keep the existing file
        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = Path(tmpdir) / "source.mp4"
            destination_file = Path(tmpdir) / "destination.mp4"

            # Create files with same size
            source_file.write_bytes(b"x" * 1000)
            destination_file.write_bytes(b"y" * 1000)

            result = self.strategy.resolve(str(source_file), str(destination_file))

            self.assertEqual(result.move_to_trash, str(source_file))
            self.assertTrue(result.skip_rename)

    def test_conflict_when_old_larger_than_new(self) -> None:
        # When old file is larger, move new to trash, rename old
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.mp4"
            new_file = Path(tmpdir) / "new.mp4"

            old_file.write_bytes(b"x" * 2000)
            new_file.write_bytes(b"y" * 1000)

            result = self.strategy.resolve(str(old_file), str(new_file))

            self.assertEqual(result.move_to_trash, str(new_file))
            self.assertFalse(result.skip_rename)

    def test_conflict_when_old_smaller_than_new(self) -> None:
        # When new file is larger, move old to trash, skip rename
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.mp4"
            new_file = Path(tmpdir) / "new.mp4"

            old_file.write_bytes(b"x" * 1000)
            new_file.write_bytes(b"y" * 2000)

            result = self.strategy.resolve(str(old_file), str(new_file))

            self.assertEqual(result.move_to_trash, str(old_file))
            self.assertTrue(result.skip_rename)

    def test_zero_byte_files_equal_size(self) -> None:
        # When both files are empty (0 bytes), trash the source file
        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = Path(tmpdir) / "source.mp4"
            destination_file = Path(tmpdir) / "destination.mp4"

            source_file.write_bytes(b"")
            destination_file.write_bytes(b"")

            result = self.strategy.resolve(str(source_file), str(destination_file))

            self.assertEqual(result.move_to_trash, str(source_file))
            self.assertTrue(result.skip_rename)

    def test_one_byte_file_vs_empty(self) -> None:
        # When one file is 1 byte, other is empty
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.mp4"
            new_file = Path(tmpdir) / "new.mp4"

            old_file.write_bytes(b"x")
            new_file.write_bytes(b"")

            result = self.strategy.resolve(str(old_file), str(new_file))

            self.assertEqual(result.move_to_trash, str(new_file))
            self.assertFalse(result.skip_rename)

    def test_large_file_vs_small_file(self) -> None:
        # When old is much larger than new
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.mp4"
            new_file = Path(tmpdir) / "new.mp4"

            old_file.write_bytes(b"x" * 1000000)  # 1MB
            new_file.write_bytes(b"y" * 1000)  # 1KB

            result = self.strategy.resolve(str(old_file), str(new_file))

            self.assertEqual(result.move_to_trash, str(new_file))
            self.assertFalse(result.skip_rename)

    def test_consistent_results_across_calls(self) -> None:
        # When calling resolve multiple times with same files
        with tempfile.TemporaryDirectory() as tmpdir:
            old_file = Path(tmpdir) / "old.mp4"
            new_file = Path(tmpdir) / "new.mp4"

            old_file.write_bytes(b"x" * 1000)
            new_file.write_bytes(b"y" * 2000)

            result1 = self.strategy.resolve(str(old_file), str(new_file))
            result2 = self.strategy.resolve(str(old_file), str(new_file))

            self.assertEqual(result1, result2)

    def test_with_mocked_missing_old_file(self) -> None:
        # When old file doesn't exist, stat() should raise
        with patch("taren.sizebasedconflictstrategy.os.path.exists", return_value=True):
            with patch("taren.sizebasedconflictstrategy.os.stat", side_effect=FileNotFoundError):
                with self.assertRaises(FileNotFoundError):
                    self.strategy.resolve("/path/to/old.mp4", "/path/to/new.mp4")

    def test_different_names_same_size(self) -> None:
        # When files have different names but same size, trash the source file
        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = Path(tmpdir) / "episode_001.mp4"
            destination_file = Path(tmpdir) / "episode_001_new.mp4"

            source_file.write_bytes(b"x" * 1000)
            destination_file.write_bytes(b"y" * 1000)

            result = self.strategy.resolve(str(source_file), str(destination_file))

            self.assertEqual(result.move_to_trash, str(source_file))
            self.assertTrue(result.skip_rename)


if __name__ == "__main__":
    unittest.main()
