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

import gc
import shutil
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
                "taren.http_timeout": "10",
                "taren.http_retries": "1",
            }
        )

    def _setup_collection(self, tmpdir: str):
        """Create downloads, seen and unseen subfolders inside the collection root."""
        downloads = Path(tmpdir) / "downloads"
        seen = Path(tmpdir) / "seen"
        unseen = Path(tmpdir) / "unseen"
        downloads.mkdir(exist_ok=True)
        seen.mkdir(exist_ok=True)
        unseen.mkdir(exist_ok=True)
        return downloads, seen, unseen

    def test_rename_process_equal_size_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0001 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, seen, _ = self._setup_collection(tmpdir)
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

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()
            del runner

            self.assertFalse(old_path.exists())
            self.assertTrue(new_path.exists())
            self.assertIn(f"{target_label}.mp4", fake_trash.moved)

    def test_rename_process_trashes_download_with_normalized_suffix_when_same_size_conflict_exists(self) -> None:
        tmpdir = tempfile.mkdtemp()
        runner = None
        try:
            target_label = "Tatort - 0005 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, seen, _ = self._setup_collection(tmpdir)
            trash = Path(tmpdir) / ".trash"
            trash.mkdir()
            (trash / f"{target_label}.mp4").write_bytes(b"existing")

            old_path = downloads / old_name
            old_path.write_bytes(b"123456")
            new_path = seen / f"{target_label}.mp4"
            new_path.write_bytes(b"abcdef")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode(target_label),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            self.assertTrue(new_path.exists())

            trashed_files = [p.name for p in trash.iterdir() if p.is_file() and p.name != ".ignore"]
            self.assertIn(f"{target_label}_02.mp4", trashed_files)
        finally:
            if runner is not None:
                del runner
            gc.collect()
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_rename_process_old_smaller_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0002 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, seen, _ = self._setup_collection(tmpdir)
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

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            self.assertTrue(new_path.exists())
            self.assertIn(f"{target_label}.mp4", fake_trash.moved)

    def test_rename_process_skips_when_already_in_seen(self) -> None:
        """File already in seen/ with correct name is counted as owned, not re-processed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0003 - A - B - C - 2020"
            old_name = f"{target_label}.mp4"
            downloads, seen, _ = self._setup_collection(tmpdir)
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

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()

            self.assertTrue(seen_path.exists())
            self.assertEqual(fake_trash.moved, [])

    def test_rename_process_old_larger_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0004 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, seen, _ = self._setup_collection(tmpdir)
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

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
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
            downloads, seen, _ = self._setup_collection(tmpdir)
            (downloads / old_name).write_bytes(b"123")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode("Tatort - 0001 - A - B - C - 2020"),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            setattr(runner, "_trash", FakeTrash(init_ok=False))

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()

            self.assertTrue((downloads / old_name).exists())

    def test_rename_process_aborts_when_cache_init_fails(self) -> None:
        # When episode cache initialization fails during _preflight()
        with tempfile.TemporaryDirectory() as tmpdir:
            downloads, _, _ = self._setup_collection(tmpdir)
            old_name = "Tatort_source.mp4"
            (downloads / old_name).write_bytes(b"123")

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            # Mock the episode_file_cache.initialize() to raise OSError
            with patch.object(runner._episode_file_cache, "initialize", side_effect=OSError("disk error")):
                with patch("taren.taren.logger.error") as log_error:
                    runner.rename_process()

                # Verify error was logged and process aborted
                self.assertTrue(log_error.called)
                # The file should not be processed (still exists in downloads)
                self.assertTrue((downloads / old_name).exists())

    def test_rename_process_skips_download_without_episode_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            old_name = "Tatort_source.mp4"
            downloads, seen, unseen = self._setup_collection(tmpdir)
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

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()

            self.assertTrue(old_path.exists())
            self.assertEqual(fake_trash.moved, [])

    def test_rename_process_uses_injected_conflict_strategy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0099 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, _, unseen = self._setup_collection(tmpdir)
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

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()

            self.assertEqual(len(strategy.calls), 1)
            self.assertFalse(old_path.exists())
            self.assertTrue((unseen / f"{target_label}.mp4").exists())

    def test_rename_process_replaces_unseen_with_larger_download_and_promotes_to_seen(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0101 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, seen, unseen = self._setup_collection(tmpdir)
            old_path = downloads / old_name
            old_path.write_bytes(b"123456")
            unseen_path = unseen / f"{target_label}.mp4"
            unseen_path.write_bytes(b"1")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode(target_label),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            # Download replaces the smaller unseen file and remains in unseen
            self.assertTrue((unseen / f"{target_label}.mp4").exists())
            # The original unseen file should have been moved to trash
            self.assertIn(f"{target_label}.mp4", fake_trash.moved)

    def test_rename_process_trashes_download_when_unseen_version_is_equal_or_larger(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0102 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, seen, unseen = self._setup_collection(tmpdir)
            old_path = downloads / old_name
            old_path.write_bytes(b"1")
            unseen_path = unseen / f"{target_label}.mp4"
            unseen_path.write_bytes(b"123456")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode(target_label),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            self.assertTrue(unseen_path.exists())
            self.assertFalse((seen / f"{target_label}.mp4").exists())
            self.assertIn(f"{target_label}.mp4", fake_trash.moved)

    def test_rename_process_trashes_download_when_unseen_version_is_equal_size(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target_label = "Tatort - 0103 - A - B - C - 2020"
            old_name = "Tatort_source.mp4"
            downloads, seen, unseen = self._setup_collection(tmpdir)
            old_path = downloads / old_name
            old_path.write_bytes(b"123456")
            unseen_path = unseen / f"{target_label}.mp4"
            unseen_path.write_bytes(b"123456")

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 1,
                find_episode=lambda _: FakeEpisode(target_label),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))
            fake_trash = FakeTrash()
            setattr(runner, "_trash", fake_trash)

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()

            self.assertFalse(old_path.exists())
            self.assertTrue(unseen_path.exists())
            self.assertFalse((seen / f"{target_label}.mp4").exists())
            self.assertIn(f"{target_label}.mp4", fake_trash.moved)

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
            downloads, seen, _ = self._setup_collection(tmpdir)
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

            # Download going to trash: renamed to normalized name first, then trashed
            commands = runner._build_commands_for_task(
                "old.mp4",
                "new.mp4",
                cast(Any, SimpleNamespace(move_to_trash="old.mp4", skip_rename=True)),
            )
            self.assertEqual(len(commands), 2)
            self.assertIsInstance(commands[0], RenameFileCommand)
            self.assertIsInstance(commands[1], MoveToTrashCommand)

            # No conflict: download renamed to destination
            commands = runner._build_commands_for_task(
                "old.mp4",
                "new.mp4",
                cast(Any, SimpleNamespace(move_to_trash=None, skip_rename=False)),
            )
            self.assertEqual(len(commands), 1)
            self.assertIsInstance(commands[0], RenameFileCommand)

            # Existing file trashed (already normalized), download renamed to destination
            commands = runner._build_commands_for_task(
                "old.mp4",
                "new.mp4",
                cast(Any, SimpleNamespace(move_to_trash="existing.mp4", skip_rename=False)),
            )
            self.assertEqual(len(commands), 2)
            self.assertIsInstance(commands[0], MoveToTrashCommand)
            self.assertIsInstance(commands[1], RenameFileCommand)

    def test_build_commands_for_task_trash_preserves_original_extension(self) -> None:
        """Rename-before-trash uses stem from new_fqn and extension from old_fqn."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            dl_dir = Path(tmpdir) / "downloads"
            old_fqn = str(dl_dir / "raw_download.mkv")
            new_fqn = str(Path(tmpdir) / "unseen" / "Tatort - Episode 1.mp4")

            commands = runner._build_commands_for_task(
                old_fqn,
                new_fqn,
                cast(Any, SimpleNamespace(move_to_trash=old_fqn, skip_rename=True)),
            )

            # Expect: RenameFileCommand → MoveToTrashCommand
            self.assertEqual(len(commands), 2)
            rename_cmd = commands[0]
            trash_cmd = commands[1]
            self.assertIsInstance(rename_cmd, RenameFileCommand)
            self.assertIsInstance(trash_cmd, MoveToTrashCommand)

            # The rename destination must use the stem from new_fqn and keep old extension
            expected_normalized = str(dl_dir / "Tatort - Episode 1.mkv")
            self.assertEqual(rename_cmd._destination_file, expected_normalized)
            # The trash command must reference the same normalized path
            self.assertEqual(trash_cmd._file_path, expected_normalized)

    def test_build_commands_for_task_trash_already_normalized_skips_rename(self) -> None:
        """No intermediate rename when old filename already matches the normalized name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            dl_dir = Path(tmpdir) / "downloads"
            # old and new have the same stem and same extension — already normalized
            old_fqn = str(dl_dir / "Tatort - Episode 1.mp4")
            new_fqn = str(Path(tmpdir) / "unseen" / "Tatort - Episode 1.mp4")

            commands = runner._build_commands_for_task(
                old_fqn,
                new_fqn,
                cast(Any, SimpleNamespace(move_to_trash=old_fqn, skip_rename=True)),
            )

            # normalized_path == old_fqn → skip the intermediate rename, only trash
            self.assertEqual(len(commands), 1)
            self.assertIsInstance(commands[0], MoveToTrashCommand)

    def test_execute_commands_stops_after_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            first_command = MagicMock()
            first_command.execute.return_value = False
            second_command = MagicMock()
            second_command.execute.return_value = True

            success = runner._execute_commands([first_command, second_command])

            first_command.execute.assert_called_once_with()
            second_command.execute.assert_not_called()
            self.assertFalse(success)

    def test_execute_commands_returns_true_when_all_commands_succeed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            first_command = MagicMock()
            first_command.execute.return_value = True
            second_command = MagicMock()
            second_command.execute.return_value = True

            success = runner._execute_commands([first_command, second_command])

            first_command.execute.assert_called_once_with()
            second_command.execute.assert_called_once_with()
            self.assertTrue(success)

    def test_rename_command_counts_failure_when_os_rename_fails(self) -> None:
        command = RenameFileCommand("/source.mp4", "/destination.mp4")

        with patch("taren.renamefilecommand.os.rename", side_effect=OSError("disk error")):
            success = command.execute()

        self.assertFalse(success)

    def test_move_to_trash_command_counts_failure_when_move_fails(self) -> None:
        fake_trash = MagicMock()
        fake_trash.move.return_value = False
        command = MoveToTrashCommand(fake_trash, "/file.mp4")

        success = command.execute()

        self.assertFalse(success)


class TestTaRenBoundaryConditions(unittest.TestCase):
    """Test TC3: Boundary conditions in TaRen processing."""

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
                "taren.http_timeout": "10",
                "taren.http_retries": "1",
            }
        )

    def _setup_collection(self, tmpdir: str):
        """Create downloads, seen and unseen subfolders inside the collection root."""
        downloads = Path(tmpdir) / "downloads"
        seen = Path(tmpdir) / "seen"
        unseen = Path(tmpdir) / "unseen"
        downloads.mkdir(exist_ok=True)
        seen.mkdir(exist_ok=True)
        unseen.mkdir(exist_ok=True)
        return downloads, seen, unseen

    def test_rename_process_handles_empty_episode_list(self) -> None:
        # When episode source returns no episodes
        with tempfile.TemporaryDirectory() as tmpdir:
            downloads, _, _ = self._setup_collection(tmpdir)
            old_name = "Tatort_source.mp4"
            (downloads / old_name).write_bytes(b"123")

            from taren.episode import Episode

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 0,
                find_episode=lambda _: Episode.empty_instance(),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()

            # File should remain in downloads since there are no episodes to match against
            self.assertTrue((downloads / old_name).exists())

    def test_rename_process_handles_zero_length_download_folder(self) -> None:
        # When downloads folder is empty (no files to process)
        with tempfile.TemporaryDirectory() as tmpdir:
            downloads, _, _ = self._setup_collection(tmpdir)
            # Deliberately don't create any files in downloads folder

            fake_episode_list = SimpleNamespace(
                get_episodes=lambda: None,
                get_episode_count=lambda: 3,
                find_episode=lambda _: FakeEpisode("Tatort - 0001 - A - B - C - 2020"),
            )

            config = self._build_config(tmpdir)
            runner = TaRen(cast(Any, config))

            with patch("taren.taren.EpisodeList", return_value=fake_episode_list):
                runner.rename_process()

            # Process completes without error even with empty downloads
            self.assertEqual(len(list(downloads.iterdir())), 0)


if __name__ == "__main__":
    unittest.main()
