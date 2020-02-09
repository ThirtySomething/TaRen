import codecs
import datetime
import logging
import os
import requests
from os import path


class WikiCache:
    def __init__(self, cachename, websiteurl, cacheage):
        self.cachename = '{}.html'.format(cachename)
        self.websiteurl = websiteurl
        self.cacheage = cacheage
        logging.debug('cache file [{}]'.format(self.cachename))
        logging.debug('websiteurl [{}]'.format(self.websiteurl))
        logging.debug('cacheage [{}]'.format(self.cacheage))

    def _cachegetage(self):
        cacheage = 0
        if path.exists(self.cachename):
            today = datetime.datetime.today()
            modified_date = datetime.datetime.fromtimestamp(
                os.path.getmtime(self.cachename))
            cacheage = (today - modified_date).days
        return cacheage

    def _cachewrite(self):
        websitecontent = requests.get(self.websiteurl).content
        with codecs.open(self.cachename, 'w', 'utf-8') as file:
            file.write(websitecontent.decode('utf-8'))
        logging.debug('saved content to cache file')

    def _cacheread(self):
        with codecs.open(self.cachename, 'r', 'utf-8') as file:
            websitecontent = file.read()
        logging.debug('read content from cache file')
        return websitecontent

    def getWebsiteFromCache(self):
        if self._cachegetage() > self.cacheage:
            os.remove(self.cachename)
            logging.debug('deleted cache file')
        if not path.exists(self.cachename):
            self._cachewrite()
        content = self._cacheread()
        return content
