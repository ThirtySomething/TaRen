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
