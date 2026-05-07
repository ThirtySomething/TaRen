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

from taren.tarendefines import TarenDefines
from taren.taren import TaRen
from taren.tarenconfig import TarenConfig
from taren.tarenruntime import TarenRuntime


class TarenRuntimeBuilder:
    """Builder for startup/runtime assembly."""

    def __init__(self, config_file: str = f"{TarenDefines.PROGRAM_NAME}.json") -> None:
        self._config_file: str = config_file

    def build_config(self) -> TarenConfig:
        config: TarenConfig = TarenConfig(self._config_file)
        config.save()
        return config

    def validate_config(self, config: TarenConfig) -> None:
        errors: list[str] = config.validate()
        if not errors:
            return
        validation_message: str = "Invalid configuration:\n- " + "\n- ".join(errors)
        raise ValueError(validation_message)

    def build_logger(self, config: TarenConfig) -> logging.Logger:
        # Setup logging for dealing with UTF-8, unfortunately not available for basicConfig
        logger_setup: logging.Logger = logging.getLogger()
        loglevel: str = config.value_get("logging", "loglevel").upper()
        logger_setup.setLevel(loglevel)
        logger_handler: logging.FileHandler = logging.FileHandler(config.value_get("logging", "logfile"), "w", "utf-8")
        logger_handler.setFormatter(logging.Formatter(config.value_get("logging", "logstring")))
        logger_setup.addHandler(logger_handler)
        return logger_setup

    def build_runner(self, config: TarenConfig) -> TaRen:
        return TaRen(config)

    def build(self) -> TarenRuntime:
        config: TarenConfig = self.build_config()
        self.validate_config(config)
        logger: logging.Logger = self.build_logger(config)
        runner: TaRen = self.build_runner(config)
        return TarenRuntime(config=config, logger=logger, runner=runner)
