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

import logging

import requests

from taren.httpfetchpolicy import HttpFetchPolicy


class RequestsHttpFetchPolicy(HttpFetchPolicy):
    """Default HTTP fetch strategy using requests with retry/timeout policy."""

    def __init__(self, timeout_seconds: float = 10.0, retries: int = 1) -> None:
        self._timeout_seconds: float = timeout_seconds
        self._retries: int = max(1, retries)

    def fetch(self, url: str, headers: dict[str, str]) -> bytes | None:
        for attempt in range(1, self._retries + 1):
            try:
                response = requests.get(
                    url, headers=headers, timeout=self._timeout_seconds
                )
                response.raise_for_status()
                return response.content
            except requests.RequestException as e:
                if attempt == self._retries:
                    logging.error("Failed to download [%s]: %s", url, e)
                    return None
                logging.warning(
                    "download attempt [%s/%s] failed for [%s]: %s",
                    attempt,
                    self._retries,
                    url,
                    e,
                )
