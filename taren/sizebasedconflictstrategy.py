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
import os

from taren.conflictresolutionresult import ConflictResolutionResult

logger = logging.getLogger(__name__)


class SizeBasedConflictStrategy:
    """Default conflict strategy based on file size comparison."""

    def resolve(self, source_file_path: str, destination_file_path: str) -> ConflictResolutionResult:
        if not os.path.exists(destination_file_path):
            return ConflictResolutionResult(move_to_trash=None, skip_rename=False)

        source_size: int = os.stat(source_file_path).st_size
        destination_size: int = os.stat(destination_file_path).st_size

        if source_size >= destination_size:
            logger.info("size_equal: trashing existing [%s]", destination_file_path)
            return ConflictResolutionResult(move_to_trash=destination_file_path, skip_rename=False)

        logger.info("download_smaller: trashing download [%s]", source_file_path)
        return ConflictResolutionResult(move_to_trash=source_file_path, skip_rename=True)
