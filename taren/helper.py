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
from pathlib import Path

logger = logging.getLogger(__name__)


class Helper:
    ############################################################################
    @staticmethod
    def ensure_directory(dirname: str) -> bool:
        path = Path(dirname)
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug("Directory [%s] created", dirname)
            return True
        except OSError:
            logger.error("Creation of the directory [%s] failed, abort", dirname)
            return False

    ############################################################################
    @staticmethod
    def delete_file(filename: str) -> bool:
        path = Path(filename)
        if not path.exists():
            logger.debug("File [%s] does not exist, nothing to delete", filename)
            return False
        try:
            path.unlink()
            logger.debug("File [%s] deleted", filename)
            return True
        except OSError:
            logger.error("Failed to delete file [%s]", filename)
            return False

    ############################################################################
    @staticmethod
    def normalize_extension(extension: str) -> str:
        """
        Ensure extension starts with a dot.

        Args:
            extension: File extension, with or without leading dot

        Returns:
            Extension with leading dot
        """
        return extension if extension.startswith(".") else f".{extension}"
