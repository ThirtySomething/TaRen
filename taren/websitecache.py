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

import codecs
import datetime
import logging
import os
from os import path
import requests


class WebSiteCache:
    '''
    Simple file cache for websites
    '''

    def __init__(self, cachename, websiteurl, cacheage):
        '''
        Default init of variables
        '''
        self.cachename = '{}.html'.format(cachename)
        self.websiteurl = websiteurl
        self.cacheage = cacheage
        logging.debug('cache file [%s]', '{}'.format(self.cachename))
        logging.debug('websiteurl [%s]', '{}'.format(self.websiteurl))
        logging.debug('cacheage [%s]', '{}'.format(self.cacheage))

    def _get_age_in_days(self):
        '''
        Determine age in days of cached file
        '''
        cacheage = 0
        if path.exists(self.cachename):
            today = datetime.datetime.today()
            modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(self.cachename))
            cacheage = (today - modified_date).days
        logging.info('cache file [%s] aged (%s) days', '{}'.format(self.cachename), '{}'.format(cacheage))
        return cacheage

    def _write_to_cache(self):
        '''
        Write downloaded content to cache file
        '''
        websitecontent = requests.get(self.websiteurl).content
        with codecs.open(self.cachename, 'w', 'utf-8') as file:
            file.write(websitecontent.decode('utf-8'))
        logging.info('saved content to cache file [%s]', '{}'.format(self.cachename))

    def _read_from_cache(self):
        '''
        Read content from cached file
        '''
        with codecs.open(self.cachename, 'r', 'utf-8') as file:
            websitecontent = file.read()
        logging.info('read content from cache file [%s]', '{}'.format(self.cachename))
        return websitecontent

    def get_website_from_cache(self):
        '''
        First check cache file, if creation age is greater than given limit, then remove
        cache file. If cache file does not exist, retrieve website content and save to
        cache file. Retrieve content from cache file. Return content.
        '''
        if self._get_age_in_days() > self.cacheage:
            os.remove(self.cachename)
            logging.info('deleted cache file [%s]', '{}'.format(self.cachename))
        if not path.exists(self.cachename):
            self._write_to_cache()
        content = self._read_from_cache()
        return content
