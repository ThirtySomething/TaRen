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

import logging
from taren import TaRen

# Setup logging for dealing with UTF-8, unfortunately not available for basicConfig
LOGGER_SETUP = logging.getLogger()
LOGGER_SETUP.setLevel(logging.DEBUG)
LOGGER_HANDLER = logging.FileHandler('program.log', 'w', 'utf-8')
LOGGER_HANDLER.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s:%(funcName)s | %(message)s'))
LOGGER_SETUP.addHandler(LOGGER_HANDLER)

# Script to rename files downloaded with MediathekView to a specific format
if __name__ == '__main__':
    logging.debug('startup')

    # Initialize program with
    # - Location of downloads
    # - Search pattern
    # - File extension
    # - URL to list of episodes
    # - Maximum cache age in days
    DATA = TaRen('V:', 'Tatort', 'mp4', 'https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen', 1)

    # Start magic process :D
    DATA.rename_process()
