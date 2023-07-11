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

import logging.config
import logging

from taren.taren import TaRen
from taren.tarenconfig import TarenConfig
from taren.grouping import Grouping

TAREN_CONFIG = TarenConfig("program.json")
TAREN_CONFIG.save()

# Setup logging for dealing with UTF-8, unfortunately not available for basicConfig
LOGGER_SETUP = logging.getLogger()
LOGGER_SETUP.setLevel(TAREN_CONFIG.logging_loglevel.upper())
LOGGER_HANDLER = logging.FileHandler(TAREN_CONFIG.logging_logfile, "w", "utf-8")
LOGGER_HANDLER.setFormatter(logging.Formatter(TAREN_CONFIG.logging_logstring))
LOGGER_SETUP.addHandler(LOGGER_HANDLER)

# Script to rename files downloaded with MediathekView to a specific format
if __name__ == "__main__":
    logging.debug("startup")

    logging.info("Loglevel is set to [{}]".format(TAREN_CONFIG.logging_loglevel.upper()))

    # Initialize program with
    # - Location of downloads
    # - Search pattern
    # - Filename of teamlist cache
    # - File extension
    # - URL to list of episodes
    # - URL to list of teams
    # - Maximum age in days of cache file
    # - Trash folder
    # - Days to keep downloads/episodes in trash folder
    DATA = TaRen(
        TAREN_CONFIG.taren_downloads,
        TAREN_CONFIG.taren_pattern,
        TAREN_CONFIG.taren_teamlist,
        TAREN_CONFIG.taren_extension,
        TAREN_CONFIG.taren_wiki,
        TAREN_CONFIG.taren_wiki_team,
        int(TAREN_CONFIG.taren_maxcache),
        TAREN_CONFIG.taren_trash,
        int(TAREN_CONFIG.taren_trashage),
    )

    # Start magic process :D
    DATA.rename_process()

    # Create page with grouped information
    # GROUPING: Grouping = Grouping(TAREN_CONFIG)
    # GROUPING.process()
