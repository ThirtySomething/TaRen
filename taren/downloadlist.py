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


class DownloadList:
    """
    Build list of filenames
    """

    ############################################################################
    def __init__(self: object, searchdir: str, pattern: str, extension: str) -> None:
        """
        Init of variables
        """
        self._searchdir: str = searchdir
        self._pattern: str = pattern
        self._extension: str = extension
        # Ensure extenstion starts with a dot
        if not self._extension.startswith("."):
            self._extension = ".{}".format(self._extension)
        logging.debug("searchdir [{}]".format(self._searchdir))
        logging.debug("pattern [{}]".format(self._pattern))
        logging.debug("extension [{}]".format(self._extension))

    ############################################################################
    def get_filenames(self: object) -> list[str]:
        """
        Retrieve list of affected downloads
        """
        # Create search pattern
        searchpattern: str = "*{}*{}".format(self._pattern, self._extension)
        # Apply search pattern on search
        files: list[str] = fnmatch.filter(os.listdir(self._searchdir), searchpattern)
        files.sort()
        # Log info about found files
        logging.info("total number of downloads [{}]".format(len(files)))
        return files
