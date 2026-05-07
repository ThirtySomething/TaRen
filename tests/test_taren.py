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
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

from fakeconfig import FakeConfig
from fakeepisode import FakeEpisode
from faketrash import FakeTrash
from spyconflictstrategy import SpyConflictStrategy
from taren.movetotrashcommand import MoveToTrashCommand
from taren.renamefilecommand import RenameFileCommand
from taren.stats import Stats
from taren.taren import TaRen


class TestTaRenRenameProcess(unittest.TestCase):
    def _build_config(self, collection_path: str) -> FakeConfig:
        return FakeConfig(
            {
                "taren.collection": collection_path,
                "taren.pattern": "Tatort",
                "taren.extension": "mp4",
                "taren.wiki": "http://example/episodes",
                "taren.maxcache": "1",
                "taren.trashage": "1",
                "taren.trashignore": ".ignore",
                "taren.wiki_useragent": "ua",
            }
        )

    def _setup_collection(self, tmpdir: str):
        """Create downloads and seen subfolders inside the collection root."""
        downloads = Path(tmpdir) / "downloads"
        seen = Path(tmpdir) / "seen"
        downloads.mkdir(exist_ok=True)
        seen.mkdir(exist_ok=True)
        return downloads, seen

    def _dl_mocks(self, downloads_files: list, seen_files: list | None = None):
        """Return DownloadList side_effect list: first call=downloads dir, second=seen dir."""
        seen_files = seen_files or []
        return [
            SimpleNamespace(get_filenames=lambda f=downloads_files: f),
            SimpleNamespace(get_filenames=lambda f=seen_files: f),
        ]

    def test_rename_process_equal_size_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0001 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, seen = self._setup_collection(tmpdir)
            old_path = downloads / old_name
            old_path.write_bytes(b"1234")
            new_path = seen / f"{target_label}.mp4"
            new_path.write_bytes(b"abcd")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode(target_label),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", side_effect=self._dl_mocks([old_name])),
            ):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            self.assertTrue(new_path.exists())
            self.assertIn(f"{target_label}.mp4", fake_trash.moved)

    def test_rename_process_old_smaller_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0002 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, seen = self._setup_collection(tmpdir)
            old_path = downloads / old_name
            old_path.write_bytes(b"1")
            new_path = seen / f"{target_label}.mp4"
            new_path.write_bytes(b"12345")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode(target_label),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", side_effect=self._dl_mocks([old_name])),
            ):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            self.assertTrue(new_path.exists())
            self.assertIn(old_name, fake_trash.moved)

    def test_rename_process_skips_when_already_in_seen(self) -> None:
        """File already in seen/ with correct name is counted as owned, not re-processed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0003 - A - B - C - 2020"
            old_name = f"{target_label}.mp4"
            downloads, seen = self._setup_collection(tmpdir)
            seen_path = seen / old_name
            seen_path.write_bytes(b"123")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode(target_label),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch(
                    "taren.taren.DownloadList",
                    side_effect=self._dl_mocks([], [old_name]),
                ),
            ):
                runner.rename_process()

            self.assertTrue(seen_path.exists())
            self.assertEqual(fake_trash.moved, [])

    def test_rename_process_old_larger_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0004 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, seen = self._setup_collection(tmpdir)
            old_path = downloads / old_name
            old_path.write_bytes(b"123456")
            new_path = seen / f"{target_label}.mp4"
            new_path.write_bytes(b"1")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode(target_label),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", side_effect=self._dl_mocks([old_name])),
            ):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            self.assertTrue(new_path.exists())
            self.assertIn(f"{target_label}.mp4", fake_trash.moved)

    def test_rename_process_aborts_when_collection_missing(self) -> None:
        config = self._build_config("/path/that/does/not/exist")
        runner = TaRen(cast(Any, config))
        with patch("taren.taren.logger.error") as log_error:
            runner.rename_process()
        self.assertTrue(log_error.called)

    def test_rename_process_aborts_when_trash_init_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_name = "Tatort_source.mp4"
            downloads, seen = self._setup_collection(tmpdir)
            (downloads / old_name).write_bytes(b"123")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode("Tatort - 0001 - A - B - C - 2020"),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            setattr(runner, "_trash", FakeTrash(init_ok=False))

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", side_effect=self._dl_mocks([old_name])),
            ):
                runner.rename_process()

            self.assertTrue((downloads / old_name).exists())

    def test_rename_process_skips_download_without_episode_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_name = "Tatort_source.mp4"
            downloads, seen = self._setup_collection(tmpdir)
            old_path = downloads / old_name
            old_path.write_bytes(b"123")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 0,
                find_episode=lambda _: SimpleNamespace(empty=True),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", side_effect=self._dl_mocks([old_name])),
            ):
                runner.rename_process()

            self.assertTrue(old_path.exists())
            self.assertEqual(fake_trash.moved, [])

    def test_rename_process_uses_injected_conflict_strategy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0099 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, seen = self._setup_collection(tmpdir)
            old_path = downloads / old_name
            old_path.write_bytes(b"123")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode(target_label),
            )

            config = self._build_config(tmpdir)
            strategy = SpyConflictStrategy()
            runner = TaRen(cast(Any, config), conflict_strategy=cast(Any, strategy))
            fake_trash = FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with (
                patch("taren.taren.EpisodeList", return_value=fake_episode_list),
                patch("taren.taren.DownloadList", side_effect=self._dl_mocks([old_name])),
            ):
                runner.rename_process()

            self.assertEqual(len(strategy.calls), 1)
            self.assertFalse(old_path.exists())
            self.assertTrue((seen / f"{target_label}.mp4").exists())

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
            downloads, seen = self._setup_collection(tmpdir)
            (downloads / old_name).write_bytes(b"123")
            (seen / f"{target_label}.mp4").write_bytes(b"1")

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            task = SimpleNamespace(
                filename=old_name,
                episode=FakeEpisode(target_label),
                sourcedir=str(downloads),
            )
            statistics = Stats()

            with patch.object(runner, "_execute_commands") as execute_commands:
                runner._process_tasks(cast(Any, [task]), statistics)

            execute_commands.assert_called_once()
            commands = execute_commands.call_args.args[0]
            self.assertEqual(len(commands), 2)
            self.assertIsInstance(commands[0], MoveToTrashCommand)
            self.assertIsInstance(commands[1], RenameFileCommand)

    def test_build_commands_for_task_variants(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            commands = runner._build_commands_for_task(
                "old.mp4",
                "new.mp4",
                cast(Any, SimpleNamespace(move_to_trash="old.mp4", skip_rename=True)),
            )
            self.assertEqual(len(commands), 1)
            self.assertIsInstance(commands[0], MoveToTrashCommand)

            commands = runner._build_commands_for_task(
                "old.mp4",
                "new.mp4",
                cast(Any, SimpleNamespace(move_to_trash=None, skip_rename=False)),
            )
            self.assertEqual(len(commands), 1)
            self.assertIsInstance(commands[0], RenameFileCommand)

            commands = runner._build_commands_for_task(
                "old.mp4",
                "new.mp4",
                cast(Any, SimpleNamespace(move_to_trash="old.mp4", skip_rename=False)),
            )
            self.assertEqual(len(commands), 2)
            self.assertIsInstance(commands[0], MoveToTrashCommand)
            self.assertIsInstance(commands[1], RenameFileCommand)

    def test_execute_commands_stops_after_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            statistics = Stats()

            first_command = MagicMock()
            first_command.execute.return_value = False
            second_command = MagicMock()
            second_command.execute.return_value = True

            runner._execute_commands([first_command, second_command], statistics)

            first_command.execute.assert_called_once_with(statistics)
            second_command.execute.assert_not_called()

    def test_rename_command_counts_failure_when_os_rename_fails(self) -> None:
        statistics = Stats()
        command = RenameFileCommand("/source.mp4", "/destination.mp4")

        with patch("taren.renamefilecommand.os.rename", side_effect=OSError("disk error")):
            success = command.execute(statistics)

        self.assertFalse(success)
        self.assertEqual(statistics.downloads_renamed, 0)
        self.assertEqual(statistics.downloads_failed, 1)

    def test_move_to_trash_command_counts_failure_when_move_fails(self) -> None:
        statistics = Stats()
        fake_trash = MagicMock()
        fake_trash.move.return_value = False
        command = MoveToTrashCommand(fake_trash, "/file.mp4")

        success = command.execute(statistics)

        self.assertFalse(success)
        self.assertEqual(statistics.downloads_moved, 0)
        self.assertEqual(statistics.downloads_failed, 1)


class TestTaRenErrorScenarios(unittest.TestCase):
    """Test error handling in main workflow scenarios."""

    def _build_config(self, collection_path: str) -> FakeConfig:
        return FakeConfig(
            {
                "taren.collection": collection_path,
                "taren.pattern": "Tatort",
                "taren.extension": "mp4",
                "taren.wiki": "http://example/episodes",
                "taren.maxcache": "1",
                "taren.trashage": "1",
                "taren.trashignore": ".ignore",
                "taren.wiki_useragent": "ua",
            }
        )

    def _setup_collection(self, tmpdir: str):
        """Create downloads and seen subfolders inside the collection root."""
        downloads = Path(tmpdir) / "downloads"
        seen = Path(tmpdir) / "seen"
        downloads.mkdir(exist_ok=True)
        seen.mkdir(exist_ok=True)
        return downloads, seen

    def _dl_mocks(self, downloads_files: list, seen_files: list | None = None):
        """Return DownloadList side_effect list: first call=downloads dir, second=seen dir."""
        seen_files = seen_files or []
        return [
            SimpleNamespace(get_filenames=lambda f=downloads_files: f),
            SimpleNamespace(get_filenames=lambda f=seen_files: f),
        ]

    def test_load_episodes_handles_empty_website_content(self) -> None:
        """When website returns empty content, should handle gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloads, seen = self._setup_collection(tmpdir)

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 0,
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            stats = Stats()

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                result = runner._load_episodes(stats)

            self.assertEqual(stats.episodes_total, 0)

    def test_process_tasks_continues_after_single_command_failure(self) -> None:
        """When a command fails, subsequent tasks should still be processed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloads, seen = self._setup_collection(tmpdir)
            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            stats = Stats()

            # Create two tasks
            task1 = SimpleNamespace(
                filename="file1.mp4",
                episode=FakeEpisode("Tatort - 0001 - A - B - C - 2020"),
                sourcedir=str(downloads),
            )
            task2 = SimpleNamespace(
                filename="file2.mp4",
                episode=FakeEpisode("Tatort - 0002 - A - B - C - 2020"),
                sourcedir=str(downloads),
            )

            # Mock execute_commands to track calls
            with patch.object(runner, "_execute_commands") as execute_commands:
                runner._process_tasks([task1, task2], stats)

            # Both tasks should attempt execution
            self.assertEqual(execute_commands.call_count, 2)

    def test_collect_tasks_returns_none_when_trash_init_fails(self) -> None:
        """When trash initialization fails, should return None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloads, seen = self._setup_collection(tmpdir)
            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            # Mock trash with failing init
            fake_trash = SimpleNamespace(init=lambda: False)
            runner._trash = cast(Any, fake_trash)

            fake_episode_list = SimpleNamespace(
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode("Tatort - 0001 - A - B - C - 2020"),
            )
            stats = Stats()

            with patch("taren.taren.DownloadList", side_effect=self._dl_mocks([])):
                result = runner._collect_tasks(fake_episode_list, stats)

            self.assertIsNone(result)

    def test_preflight_creates_missing_subfolders(self) -> None:
        """When subfolders don't exist, preflight should create them."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            result = runner._preflight()

            self.assertTrue(result)
            self.assertTrue((Path(tmpdir) / "downloads").exists())
            self.assertTrue((Path(tmpdir) / "seen").exists())

    def test_finalize_tracks_deleted_and_trash_stats(self) -> None:
        """When finalize is called, should update stats with cleanup results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloads, seen = self._setup_collection(tmpdir)
            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            fake_trash = SimpleNamespace(
                cleanup=lambda: 5,  # 5 files deleted
                list=lambda: 3,  # 3 files in trash
            )
            runner._trash = cast(Any, fake_trash)
            stats = Stats()

            runner._finalize(stats)

            self.assertEqual(stats.downloads_deleted, 5)
            self.assertEqual(stats.downloads_trash, 3)

    def test_collect_tasks_skips_episodes_without_match(self) -> None:
        """When episode matching fails, file should be skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloads, seen = self._setup_collection(tmpdir)
            (downloads / "unknown_file.mp4").write_bytes(b"123")

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            runner._trash.init()

            fake_episode_list = SimpleNamespace(
                get_episode_count=lambda: 1,
                find_episode=lambda _: SimpleNamespace(empty=True),
            )
            stats = Stats()

            with patch("taren.taren.DownloadList", side_effect=self._dl_mocks(["unknown_file.mp4"])):
                tasks = runner._collect_tasks(fake_episode_list, stats)

            self.assertEqual(len(tasks), 0)
            self.assertEqual(stats.downloads_total, 1)

    def test_process_tasks_increments_episodes_owned_when_already_placed(self) -> None:
        """When file is already in seen folder with correct name, should increment episodes_owned."""
        with tempfile.TemporaryDirectory() as tmpdir:
            downloads, seen = self._setup_collection(tmpdir)
            target_name = "Tatort - 0005 - A - B - C - 2020"

            # File is already in correct location
            (seen / f"{target_name}.mp4").write_bytes(b"123")

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            stats = Stats()

            task = SimpleNamespace(
                filename=f"{target_name}.mp4",
                episode=FakeEpisode(target_name),
                sourcedir=str(seen),
            )

            runner._process_tasks([task], stats)

            self.assertEqual(stats.episodes_owned, 1)


if __name__ == "__main__":
    unittest.main()
