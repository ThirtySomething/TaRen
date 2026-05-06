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

from taren.episodesource import EpisodeSource
from taren.httpfetchpolicy import HttpFetchPolicy
from taren.websitecache import WebSiteCache


class CachedHtmlEpisodeSource(EpisodeSource):
    """Adapter for retrieving episode HTML via website cache."""

    def __init__(
        self,
        pattern: str,
        url: str,
        cachetime: int,
        useragent: str,
        fetch_policy: HttpFetchPolicy | None = None,
    ) -> None:
        self._cache: WebSiteCache = WebSiteCache(
            pattern,
            url,
            cachetime,
            useragent,
            fetch_policy=fetch_policy,
        )

    def fetch(self) -> str:
        return self._cache.get_website_from_cache()
