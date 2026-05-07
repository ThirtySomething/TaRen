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
from datetime import datetime
import hashlib
import logging
from pathlib import Path

from taren.helper import Helper
from taren.httpfetchpolicy import HttpFetchPolicy
from taren.requestshttpfetchpolicy import RequestsHttpFetchPolicy
from taren.tarendefines import TarenDefines

logger = logging.getLogger(__name__)


class WebSiteCache:
    """
    Simple file cache for websites
    """

    ############################################################################
    def __init__(
        self,
        cachename: str,
        websiteurl: str,
        cacheage: int,
        useragent: str,
        fetch_policy: HttpFetchPolicy | None = None,
        cache_dir: str | None = None,
    ) -> None:
        """
        Default init of variables
        """
        self._cacheage: int = cacheage
        # Use URL hash to prevent cache collisions when identical cache stems
        # are used with different URLs (for example different show pages).
        url_hash: str = hashlib.md5(websiteurl.encode()).hexdigest()[: TarenDefines.URL_HASH_LENGTH]
        cache_stem: str = Path(cachename).name
        cache_filename: str = f"{cache_stem}_{url_hash}.html"
        if cache_dir:
            self._cache_path: Path = Path(cache_dir) / cache_filename
        else:
            self._cache_path = Path(cachename).with_name(cache_filename)
        self._cachename: str = str(self._cache_path)
        self._websiteurl: str = websiteurl
        self._useragent: str = useragent
        self._fetch_policy: HttpFetchPolicy = fetch_policy or RequestsHttpFetchPolicy()
        logger.debug(
            "cache_init: file=%s max_age_days=%s url=%s useragent=%s status=ready",
            self._cachename,
            self._cacheage,
            self._websiteurl,
            self._useragent,
        )

    ############################################################################
    def _get_age_in_days(self) -> int:
        """
        Determine age in days of cached file
        """
        cacheage: int = 0
        if self._cache_path.exists():
            today: datetime = datetime.today()
            modified_date: datetime = datetime.fromtimestamp(self._cache_path.stat().st_mtime)
            cacheage = (today - modified_date).days
        logger.info(
            "cache_lookup: file=%s age_days=%s max_age_days=%s status=checked",
            self._cachename,
            cacheage,
            self._cacheage,
        )
        return cacheage

    ############################################################################
    def _read_from_cache(self) -> str:
        """
        Read content from cached file
        """
        with codecs.open(self._cache_path, "r", "utf-8") as file:
            websitecontent: str = file.read()
        logger.info("cache_read: file=%s status=success", self._cachename)
        return websitecontent

    ############################################################################
    def _write_to_cache(self) -> None:
        """
        Write downloaded content to cache file
        """
        headers = {"User-Agent": self._useragent}
        websitecontent: bytes | None = self._fetch_policy.fetch(self._websiteurl, headers)
        if websitecontent is None:
            return
        try:
            decoded_content: str = websitecontent.decode("utf-8")
        except UnicodeDecodeError as exc:
            logger.error(
                "cache_write: url=%s file=%s status=failed reason=utf8_decode error=%s",
                self._websiteurl,
                self._cachename,
                exc,
            )
            return
        with codecs.open(self._cache_path, "w", "utf-8") as file:
            file.write(decoded_content)
        logger.info("cache_write: url=%s file=%s status=success", self._websiteurl, self._cachename)

    ############################################################################
    def get_website_from_cache(self) -> str:
        """
        First check cache file, if creation age is greater than given limit, then remove
        cache file. If cache file does not exist, retrieve website content and save to
        cache file. Retrieve content from cache file. Return content.
        """
        if self._get_age_in_days() > self._cacheage:
            Helper.delete_file(self._cachename)
            logger.info("cache_eviction: file=%s status=deleted", self._cachename)
        if not self._cache_path.exists():
            self._write_to_cache()
        if not self._cache_path.exists():
            logger.error("cache_lookup: file=%s status=failed reason=download_unavailable", self._cachename)
            return ""
        content: str = self._read_from_cache()
        return content
