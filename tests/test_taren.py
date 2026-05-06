import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import patch

from taren.taren import MoveToTrashCommand, RenameFileCommand, TaRen
from taren.stats import Stats


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
    def __init__(self, init_ok: bool = True) -> None:
        self._init_ok = init_ok
        self.moved: list[str] = []

    def init(self) -> bool:
        return self._init_ok

    def move(self, file_path: str) -> None:
        self.moved.append(os.path.basename(file_path))
        if os.path.exists(file_path):
            os.remove(file_path)

    def cleanup(self) -> int:
        return 0

    def list(self) -> int:
        return 0


class _SpyConflictStrategy:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def resolve(self, old_fqn: str, new_fqn: str):
        self.calls.append((old_fqn, new_fqn))
        return SimpleNamespace(move_to_trash=None, skip_rename=False)


class TestTaRenRenameProcess(unittest.TestCase):
    def _build_config(self, downloads_path: str) -> _FakeConfig:
        return _FakeConfig(
            {
                "taren.downloads": downloads_path,
                "taren.pattern": "Tatort",
                "taren.extension": "mp4",
                "taren.wiki": "http://example/episodes",
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

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", return_value=fake_download_list),
            ):
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

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", return_value=fake_download_list),
            ):
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

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", return_value=fake_download_list),
            ):
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

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", return_value=fake_download_list),
            ):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            self.assertTrue(new_path.exists())
            self.assertIn(f"{target_label}.mp4", fake_trash.moved)

    def test_rename_process_aborts_when_searchdir_missing(self) -> None:
        config = self._build_config("/path/that/does/not/exist")
        runner = TaRen(cast(Any, config))
        with patch("taren.taren.logging.error") as log_error:
            runner.rename_process()
        self.assertTrue(log_error.called)

    def test_rename_process_aborts_when_trash_init_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_name = "Tatort_source.mp4"
            Path(tmpdir, old_name).write_bytes(b"123")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: _FakeEpisode("Tatort - 0001 - A - B - C - 2020"),
            )
            fake_download_list = SimpleNamespace(get_filenames=lambda: [old_name])

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            setattr(runner, "_trash", _FakeTrash(init_ok=False))

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", return_value=fake_download_list),
            ):
                runner.rename_process()

            self.assertTrue(Path(tmpdir, old_name).exists())

    def test_rename_process_skips_download_without_episode_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_name = "Tatort_source.mp4"
            old_path = Path(tmpdir) / old_name
            old_path.write_bytes(b"123")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 0,
                find_episode=lambda _: SimpleNamespace(empty=True),
            )
            fake_download_list = SimpleNamespace(get_filenames=lambda: [old_name])

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = _FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", return_value=fake_download_list),
            ):
                runner.rename_process()

            self.assertTrue(old_path.exists())
            self.assertEqual(fake_trash.moved, [])

    def test_rename_process_uses_injected_conflict_strategy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0099 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            old_path = Path(tmpdir) / old_name
            old_path.write_bytes(b"123")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: _FakeEpisode(target_label),
            )
            fake_download_list = SimpleNamespace(get_filenames=lambda: [old_name])

            config = self._build_config(tmpdir)
            strategy = _SpyConflictStrategy()
            runner = TaRen(cast(Any, config), conflict_strategy=cast(Any, strategy))
            fake_trash = _FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", return_value=fake_download_list),
            ):
                runner.rename_process()

            self.assertEqual(len(strategy.calls), 1)
            self.assertFalse(old_path.exists())
            self.assertTrue(Path(tmpdir, f"{target_label}.mp4").exists())

    def test_rename_process_uses_template_pipeline_methods(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            fake_episode_list = SimpleNamespace()

            with (
                patch.object(runner, "_preflight", return_value=True) as preflight,
                patch.object(runner, "_load_episodes", return_value=fake_episode_list) as load_episodes,
                patch.object(runner, "_collect_tasks", return_value=[]) as collect_tasks,
                patch.object(runner, "_process_tasks") as process_tasks,
                patch.object(runner, "_finalize") as finalize,
            ):
                runner.rename_process()

            preflight.assert_called_once_with()
            load_episodes.assert_called_once()
            self.assertIsInstance(load_episodes.call_args.args[0], Stats)
            collect_tasks.assert_called_once_with(fake_episode_list, load_episodes.call_args.args[0])
            process_tasks.assert_called_once_with([], load_episodes.call_args.args[0])
            finalize.assert_called_once_with(load_episodes.call_args.args[0])

    def test_process_tasks_builds_expected_commands_on_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0010 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            old_path = Path(tmpdir) / old_name
            old_path.write_bytes(b"123")
            new_path = Path(tmpdir) / f"{target_label}.mp4"
            new_path.write_bytes(b"1")

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            task = SimpleNamespace(filename=old_name, episode=_FakeEpisode(target_label))
            statistics = Stats()

            with patch.object(runner, "_execute_commands") as execute_commands:
                runner._process_tasks([task], statistics)

            execute_commands.assert_called_once()
            commands = execute_commands.call_args.args[0]
            self.assertEqual(len(commands), 2)
            self.assertIsInstance(commands[0], MoveToTrashCommand)
            self.assertIsInstance(commands[1], RenameFileCommand)


if __name__ == "__main__":
    unittest.main()
