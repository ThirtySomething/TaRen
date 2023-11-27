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

import codecs
import datetime
import logging
import os

import requests

from taren.helper import Helper


class WebSiteCache:
    """
    Simple file cache for websites
    """

    ############################################################################
    def __init__(self: object, cachename: str, websiteurl: str, cacheage: int) -> None:
        """
        Default init of variables
        """
        self._cacheage: int = cacheage
        self._cachename: str = "{}.html".format(cachename)
        self._websiteurl: str = websiteurl
        logging.debug("cache file [{}]".format(self._cachename))
        logging.debug("cacheage [{}]".format(self._cacheage))
        logging.debug("websiteurl [{}]".format(self._websiteurl))

    ############################################################################
    def _get_age_in_days(self: object) -> int:
        """
        Determine age in days of cached file
        """
        cacheage: int = 0
        if os.path.exists(self._cachename):
            today: datetime = datetime.datetime.today()
            modified_date: datetime = datetime.datetime.fromtimestamp(os.path.getmtime(self._cachename))
            cacheage = (today - modified_date).days
        logging.info("cache file [{}] aged [{}] days, maxage [{}] days".format(self._cachename, cacheage, self._cacheage))
        return cacheage

    ############################################################################
    def _read_from_cache(self: object) -> str:
        """
        Read content from cached file
        """
        with codecs.open(self._cachename, "r", "utf-8") as file:
            websitecontent: str = file.read()
        logging.info("read content from cache file [{}]".format(self._cachename))
        return websitecontent

    ############################################################################
    def _write_to_cache(self: object) -> None:
        """
        Write downloaded content to cache file
        """
        websitecontent: bytes = requests.get(self._websiteurl).content
        with codecs.open(self._cachename, "w", "utf-8") as file:
            file.write(websitecontent.decode("utf-8"))
        logging.info("saved content of [{}] to cache file [{}]".format(self._websiteurl, self._cachename))

    ############################################################################
    def get_website_from_cache(self: object) -> str:
        """
        First check cache file, if creation age is greater than given limit, then remove
        cache file. If cache file does not exist, retrieve website content and save to
        cache file. Retrieve content from cache file. Return content.
        """
        if self._get_age_in_days() > self._cacheage:
            Helper.delete_file(self._cachename)
            logging.info("deleted cache file [{}]".format(self._cachename))
        if not os.path.exists(self._cachename):
            self._write_to_cache()
        content: str = self._read_from_cache()
        return content
