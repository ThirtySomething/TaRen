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

            dl = DownloadList(tmpdir, "Tatort", ".mp4")
            self.assertEqual(dl.get_filenames(), ["Tatort_A.mp4", "Tatort_B.mp4"])


if __name__ == "__main__":
    unittest.main()
