import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from taren.taren import TaRen


class _FakeConfig:
    def __init__(self, values: dict[str, str]) -> None:
        self._values = values

    def value_get(self, section: str, key: str) -> str:
        return self._values[f"{section}.{key}"]


class _FakeEpisode:
    def __init__(self, label: str) -> None:
        self.empty = False
        self._label = label

    def __str__(self) -> str:
        return self._label


class _FakeTrash:
    def __init__(self) -> None:
        self.moved: list[str] = []

    def init(self) -> bool:
        return True

    def move(self, file_path: str) -> None:
        self.moved.append(os.path.basename(file_path))
        if os.path.exists(file_path):
            os.remove(file_path)

    def cleanup(self) -> int:
        return 0

    def list(self) -> int:
        return 0


class TestTaRenRenameProcess(unittest.TestCase):
    def _build_config(self, downloads_path: str) -> _FakeConfig:
        return _FakeConfig(
            {
                "taren.downloads": downloads_path,
                "taren.pattern": "Tatort",
                "taren.teamlist": "Teams",
                "taren.extension": "mp4",
                "taren.wiki": "http://example/episodes",
                "taren.wiki_team": "http://example/teams",
                "taren.maxcache": "1",
                "taren.trashage": "1",
                "taren.trashignore": ".ignore",
                "taren.trash": ".trash",
                "taren.wiki_useragent": "ua",
            }
        )

    def test_rename_process_equal_size_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0001 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            old_path = Path(tmpdir) / old_name
            old_path.write_bytes(b"1234")
            new_path = Path(tmpdir) / f"{target_label}.mp4"
            new_path.write_bytes(b"abcd")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: _FakeEpisode(target_label),
            )
            fake_download_list = SimpleNamespace(get_filenames=lambda: [old_name])

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = _FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list), patch("taren.taren.DownloadList", return_value=fake_download_list):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            self.assertTrue(new_path.exists())
            self.assertIn(f"{target_label}.mp4", fake_trash.moved)

    def test_rename_process_old_smaller_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0002 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            old_path = Path(tmpdir) / old_name
            old_path.write_bytes(b"1")
            new_path = Path(tmpdir) / f"{target_label}.mp4"
            new_path.write_bytes(b"12345")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: _FakeEpisode(target_label),
            )
            fake_download_list = SimpleNamespace(get_filenames=lambda: [old_name])

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = _FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list), patch("taren.taren.DownloadList", return_value=fake_download_list):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            self.assertTrue(new_path.exists())
            self.assertIn(old_name, fake_trash.moved)

    def test_rename_process_skips_when_already_processed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0003 - A - B - C - 2020"
            old_name = f"{target_label}.mp4"
            old_path = Path(tmpdir) / old_name
            old_path.write_bytes(b"123")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: _FakeEpisode(target_label),
            )
            fake_download_list = SimpleNamespace(get_filenames=lambda: [old_name])

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = _FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list), patch("taren.taren.DownloadList", return_value=fake_download_list):
                runner.rename_process()

            self.assertTrue(old_path.exists())
            self.assertEqual(fake_trash.moved, [])

    def test_rename_process_old_larger_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0004 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            old_path = Path(tmpdir) / old_name
            old_path.write_bytes(b"123456")
            new_path = Path(tmpdir) / f"{target_label}.mp4"
            new_path.write_bytes(b"1")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: _FakeEpisode(target_label),
            )
            fake_download_list = SimpleNamespace(get_filenames=lambda: [old_name])

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = _FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list), patch("taren.taren.DownloadList", return_value=fake_download_list):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            self.assertTrue(new_path.exists())
            self.assertIn(f"{target_label}.mp4", fake_trash.moved)


if __name__ == "__main__":
    unittest.main()
