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
import fnmatch
import os


class DownloadList:
    '''
    Build list of filenames
    '''
    def __init__(self, searchdir, pattern, extension):
        self.searchdir = searchdir
        self.pattern = pattern
        self.extension = extension
        if not self.extension.startswith('.'):
            self.extension = '.{}'.format(self.extension)
        logging.debug('searchdir [%s]', '{}'.format(searchdir))
        logging.debug('pattern [%s]', '{}'.format(pattern))
        logging.debug('extension [%s]', '{}'.format(extension))

    def get_filenames(self):
        '''
        Retrieve list of affected downloads
        '''
        searchpattern = '*{}*{}'.format(self.pattern, self.extension)
        files = fnmatch.filter(os.listdir(self.searchdir), searchpattern)
        logging.info('total number of downloads [%s]', '{}'.format(len(files)))
        return files
