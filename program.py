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
loglevel: str = TAREN_CONFIG.value_get("logging", "loglevel").upper()
LOGGER_SETUP.setLevel(loglevel)
LOGGER_HANDLER = logging.FileHandler(TAREN_CONFIG.value_get("logging", "logfile"), "w", "utf-8")
LOGGER_HANDLER.setFormatter(logging.Formatter(TAREN_CONFIG.value_get("logging", "logstring")))
LOGGER_SETUP.addHandler(LOGGER_HANDLER)

# Script to rename files downloaded with MediathekView to a specific format
if __name__ == "__main__":
    logging.debug("startup")

    logging.info("Loglevel is set to [{}]".format(loglevel))

    # Initialize program with complete config
    # - Location of downloads
    # - Search pattern
    # - Filename of teamlist cache
    # - File extension
    # - URL to list of episodes
    # - URL to list of teams
    # - Maximum age in days of cache file
    # - Trash folder
    # - Days to keep downloads/episodes in trash folder
    DATA = TaRen(TAREN_CONFIG)

    # Start magic process :D
    DATA.rename_process()

    # Create page with grouped information
    # GROUPING: Grouping = Grouping(TAREN_CONFIG)
    # GROUPING.process()
