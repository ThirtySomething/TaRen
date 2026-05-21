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

import logging
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import program
import taren.tarenruntimebuilder as tarenruntimebuilder
from taren.configurationerror import ConfigurationError
from taren.tarendefines import TarenDefines


class TestProgramBuilder(unittest.TestCase):
    def test_runtime_builder_builds_config_logger_and_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            collection_dir = str(Path(tmpdir) / "collection")
            Path(collection_dir).mkdir()
        config_values = {
            ("logging", "loglevel"): "info",
            ("logging", "logfile"): f"{TarenDefines.PROGRAM_NAME}.log",
            ("logging", "logstring"): "%(message)s",
            ("taren", "collection"): collection_dir,
            ("taren", "extension"): "mp4",
            ("taren", "maxcache"): "1",
            ("taren", "pattern"): "Tatort",
            ("taren", "trashage"): "1",
            ("taren", "trashignore"): ".ignore",
            ("taren", "wiki"): "https://example.invalid/wiki",
            ("taren", "wiki_useragent"): "agent",
            ("taren", "http_timeout"): "10",
            ("taren", "http_retries"): "1",
        }

        config_instance = MagicMock()
        config_instance.value_get.side_effect = lambda section, key: config_values[(section, key)]
        config_instance.validate.return_value = []

        logger_instance = MagicMock()
        handler_instance = MagicMock()
        formatter_instance = MagicMock()
        runner_instance = MagicMock()

        with (
            patch("taren.tarenruntimebuilder.TarenConfig", return_value=config_instance) as config_cls,
            patch(
                "taren.tarenruntimebuilder.logging.getLogger",
                return_value=logger_instance,
            ),
            patch(
                "taren.tarenruntimebuilder.logging.Formatter",
                return_value=formatter_instance,
            ) as formatter_cls,
            patch("taren.tarenruntimebuilder.TaRen", return_value=runner_instance) as taren_cls,
            patch.object(
                tarenruntimebuilder.TarenRuntimeBuilder,
                "_create_file_handler",
                return_value=handler_instance,
            ) as create_handler,
            patch("taren.tarenruntimebuilder.os.path.isfile", return_value=False),
        ):
            runtime = tarenruntimebuilder.TarenRuntimeBuilder(f"{TarenDefines.PROGRAM_NAME}.json").build()

        config_cls.assert_called_once_with(f"{TarenDefines.PROGRAM_NAME}.json")
        config_instance.save.assert_called_once_with()
        config_instance.validate.assert_called_once_with()
        logger_instance.setLevel.assert_called_once_with("INFO")
        create_handler.assert_called_once_with(f"{TarenDefines.PROGRAM_NAME}.log")
        formatter_cls.assert_called_once_with("%(message)s")
        handler_instance.setFormatter.assert_called_once_with(formatter_instance)
        logger_instance.addHandler.assert_called_once_with(handler_instance)
        taren_cls.assert_called_once_with(config_instance)
        self.assertIs(runtime.config, config_instance)
        self.assertIs(runtime.logger, logger_instance)
        self.assertIs(runtime.runner, runner_instance)

    def test_main_executes_runner(self) -> None:
        runner = MagicMock()
        runtime = SimpleNamespace(config=MagicMock(), logger=MagicMock(), runner=runner)

        with patch.object(program.TarenRuntimeBuilder, "build", return_value=runtime):
            program.main()

        runner.rename_process.assert_called_once_with()

    def test_main_fails_fast_on_invalid_configuration(self) -> None:
        with patch.object(program.TarenRuntimeBuilder, "build", side_effect=ConfigurationError("invalid config")):
            with self.assertRaises(SystemExit) as exit_context:
                program.main()
        self.assertEqual(exit_context.exception.code, 1)

    def test_runtime_builder_fails_fast_when_config_validation_fails(self) -> None:
        config_instance = MagicMock()
        config_instance.validate.return_value = ["bad value"]

        builder = tarenruntimebuilder.TarenRuntimeBuilder("TaRen.json")
        with patch.object(builder, "build_config", return_value=config_instance):
            with self.assertRaises(ConfigurationError):
                builder.build()

    def test_build_logger_removes_existing_file_handler_for_same_logfile(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = str(Path(tmpdir) / "TaRen.log")

            config_instance = MagicMock()
            config_instance.value_get.side_effect = lambda section, key: {
                ("logging", "loglevel"): "info",
                ("logging", "logfile"): log_path,
                ("logging", "logstring"): "%(message)s",
            }[(section, key)]

            logger_instance = MagicMock()
            stale_handler = MagicMock(spec=logging.FileHandler)
            stale_handler.baseFilename = log_path
            other_handler = MagicMock(spec=logging.StreamHandler)
            logger_instance.handlers = [stale_handler, other_handler]
            new_handler = MagicMock(spec=logging.FileHandler)

            with (
                patch("taren.tarenruntimebuilder.logging.getLogger", return_value=logger_instance),
                patch.object(
                    tarenruntimebuilder.TarenRuntimeBuilder,
                    "_create_file_handler",
                    return_value=new_handler,
                ),
            ):
                builder = tarenruntimebuilder.TarenRuntimeBuilder("TaRen.json")
                builder.build_logger(config_instance)

            logger_instance.removeHandler.assert_called_once_with(stale_handler)
            stale_handler.close.assert_called_once_with()
            logger_instance.addHandler.assert_called_once_with(new_handler)

    def test_build_logger_idempotent_on_repeated_calls(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = str(Path(tmpdir) / "TaRen.log")

            config_instance = MagicMock()
            config_instance.value_get.side_effect = lambda section, key: {
                ("logging", "loglevel"): "info",
                ("logging", "logfile"): log_path,
                ("logging", "logstring"): "%(message)s",
            }[(section, key)]

            logger_instance = MagicMock()
            logger_instance.handlers = []

            first_handler = MagicMock(spec=logging.FileHandler)
            first_handler.baseFilename = log_path
            second_handler = MagicMock(spec=logging.FileHandler)
            second_handler.baseFilename = log_path

            def add_handler(handler):
                logger_instance.handlers.append(handler)

            def remove_handler(handler):
                logger_instance.handlers.remove(handler)

            logger_instance.addHandler.side_effect = add_handler
            logger_instance.removeHandler.side_effect = remove_handler

            with (
                patch("taren.tarenruntimebuilder.logging.getLogger", return_value=logger_instance),
                patch(
                    "taren.tarenruntimebuilder.TarenRuntimeBuilder._create_file_handler",
                    side_effect=[first_handler, second_handler],
                ),
            ):
                builder = tarenruntimebuilder.TarenRuntimeBuilder("TaRen.json")
                builder.build_logger(config_instance)
                builder.build_logger(config_instance)

            file_handlers = [h for h in logger_instance.handlers if isinstance(h, logging.FileHandler)]
            self.assertEqual(len(file_handlers), 1)
            self.assertIs(file_handlers[0], second_handler)
            first_handler.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
