from typing import Protocol


class HttpFetchPolicy(Protocol):
    def fetch(self, url: str, headers: dict[str, str]) -> bytes | None:
        """Fetch bytes for the given URL, returning None on failure."""
