'''
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
'''

import logging.config
import logging
from taren.taren import TaRen
from taren.tarenconfig import TarenConfig

TAREN_CONFIG = TarenConfig()
TAREN_CONFIG.init('program.ini')

# Setup logging for dealing with UTF-8, unfortunately not available for basicConfig
LOGGER_SETUP = logging.getLogger()
LOGGER_SETUP.setLevel(logging.INFO)
# LOGGER_SETUP.setLevel(logging.DEBUG)
LOGGER_HANDLER = logging.FileHandler(TAREN_CONFIG.getLogfile(), 'w', 'utf-8')
LOGGER_HANDLER.setFormatter(logging.Formatter(TAREN_CONFIG.getLogstring()))
LOGGER_SETUP.addHandler(LOGGER_HANDLER)

# Script to rename files downloaded with MediathekView to a specific format
if __name__ == '__main__':
    logging.debug('startup')

    # logging.info('debugFlag is set to [%s]', '{}'.format(debugFlag))

    # Initialize program with
    # - Location of downloads
    # - Search pattern
    # - File extension
    # - URL to list of episodes
    # - Maximum age in days of cache file
    # - Trash folder
    # - Days to keep downloads/episodes in trash folder
    DATA = TaRen(
        TAREN_CONFIG.getDownloads(),
        TAREN_CONFIG.getPattern(),
        TAREN_CONFIG.getExtension(),
        TAREN_CONFIG.getWiki(),
        TAREN_CONFIG.getMaxcache(),
        TAREN_CONFIG.getTrash(),
        TAREN_CONFIG.getTrashage()
    )

    # Start magic process :D
    DATA.rename_process()
