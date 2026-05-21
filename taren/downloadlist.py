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
import fnmatch
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class DownloadList:
    """
    Build list of filenames
    """

    ############################################################################
    @staticmethod
    def get_filenames(searchdir: str, pattern: str, extension: str) -> list[str]:
        """
        Retrieve list of affected downloads
        """
        # Create search pattern
        searchpattern: str = f"*{pattern}*{extension}"
        # Apply search pattern on search
        files: list[str] = fnmatch.filter(os.listdir(searchdir), searchpattern)
        files.sort()
        # Log info about found files
        logger.info(
            "collection_scan: folder=%s path=%s matched_files=%s",
            Path(searchdir).name,
            searchdir,
            len(files),
        )
        return files
