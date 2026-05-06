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
