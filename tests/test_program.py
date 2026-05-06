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

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import program
import taren.tarenruntimebuilder as tarenruntimebuilder


class TestProgramBuilder(unittest.TestCase):
    def test_runtime_builder_builds_config_logger_and_runner(self) -> None:
        config_values = {
            ("logging", "loglevel"): "info",
            ("logging", "logfile"): "program.log",
            ("logging", "logstring"): "%(message)s",
        }

        config_instance = MagicMock()
        config_instance.value_get.side_effect = lambda section, key: config_values[(section, key)]

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
                "taren.tarenruntimebuilder.logging.FileHandler",
                return_value=handler_instance,
            ) as file_handler_cls,
            patch(
                "taren.tarenruntimebuilder.logging.Formatter",
                return_value=formatter_instance,
            ) as formatter_cls,
            patch("taren.tarenruntimebuilder.TaRen", return_value=runner_instance) as taren_cls,
        ):
            runtime = tarenruntimebuilder.TarenRuntimeBuilder("program.json").build()

        config_cls.assert_called_once_with("program.json")
        config_instance.save.assert_called_once_with()
        logger_instance.setLevel.assert_called_once_with("INFO")
        file_handler_cls.assert_called_once_with("program.log", "w", "utf-8")
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


if __name__ == "__main__":
    unittest.main()
