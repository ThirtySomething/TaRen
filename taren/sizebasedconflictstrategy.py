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

    def resolve(self, old_fqn: str, new_fqn: str) -> ConflictResolutionResult:
        if not os.path.exists(new_fqn):
            return ConflictResolutionResult(move_to_trash=None, skip_rename=False)

        size_old: int = os.stat(old_fqn).st_size
        size_new: int = os.stat(new_fqn).st_size

        if size_old >= size_new:
            logger.info("size_equal: trashing existing [%s]", new_fqn)
            return ConflictResolutionResult(move_to_trash=new_fqn, skip_rename=False)

        logger.info("download_smaller: trashing download [%s]", old_fqn)
        return ConflictResolutionResult(move_to_trash=old_fqn, skip_rename=True)
