import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from taren.helper import Helper
from taren.websitecache import RequestsHttpFetchPolicy, WebSiteCache


class TestWebsiteCache(unittest.TestCase):
    class _FakePolicy:
        def __init__(self, payload: bytes | None) -> None:
            self.payload = payload
            self.calls: list[tuple[str, dict[str, str]]] = []

        def fetch(self, url: str, headers: dict[str, str]) -> bytes | None:
            self.calls.append((url, headers))
            return self.payload

    def test_write_to_cache_success_and_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = str(Path(tmpdir) / "cache")
            cache = WebSiteCache(base, "http://example", 1, "ua")

            response = MagicMock()
            response.content = b"<html>ok</html>"
            response.raise_for_status.return_value = None

            with patch("taren.websitecache.requests.get", return_value=response):
                cache._write_to_cache()
            self.assertTrue(Path(cache._cachename).exists())

            failed = WebSiteCache(str(Path(tmpdir) / "cache_fail"), "http://example", 1, "ua")
            with patch("taren.websitecache.requests.get", side_effect=Exception("boom")):
                with patch("taren.websitecache.requests.RequestException", Exception):
                    failed._write_to_cache()
            self.assertFalse(Path(failed._cachename).exists())

    def test_get_website_from_cache_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = str(Path(tmpdir) / "cache")
            cache = WebSiteCache(base, "http://example", 1, "ua")

            Path(cache._cachename).write_text("cached", encoding="utf-8")
            self.assertEqual(cache.get_website_from_cache(), "cached")

            missing = WebSiteCache(str(Path(tmpdir) / "missing"), "http://example", 1, "ua")
            with patch.object(WebSiteCache, "_write_to_cache", return_value=None):
                self.assertEqual(missing.get_website_from_cache(), "")

    def test_get_website_from_cache_deletes_stale_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = str(Path(tmpdir) / "stale")
            cache = WebSiteCache(base, "http://example", 1, "ua")
            Path(cache._cachename).write_text("stale", encoding="utf-8")

            with (
                patch.object(WebSiteCache, "_get_age_in_days", return_value=10),
                patch("taren.websitecache.Helper.delete_file", wraps=Helper.delete_file),
                patch.object(WebSiteCache, "_write_to_cache", return_value=None),
            ):
                self.assertEqual(cache.get_website_from_cache(), "")

    def test_get_website_from_cache_refreshes_stale_cache_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = str(Path(tmpdir) / "refresh")
            cache = WebSiteCache(base, "http://example", 1, "ua")
            Path(cache._cachename).write_text("old", encoding="utf-8")

            response = MagicMock()
            response.content = b"new-content"
            response.raise_for_status.return_value = None

            with (
                patch.object(WebSiteCache, "_get_age_in_days", return_value=10),
                patch("taren.websitecache.requests.get", return_value=response),
            ):
                self.assertEqual(cache.get_website_from_cache(), "new-content")

    def test_get_age_in_days_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = WebSiteCache(str(Path(tmpdir) / "age"), "http://example", 1, "ua")
            self.assertEqual(cache._get_age_in_days(), 0)

            Path(cache._cachename).write_text("x", encoding="utf-8")
            self.assertGreaterEqual(cache._get_age_in_days(), 0)

    def test_write_to_cache_uses_injected_fetch_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = str(Path(tmpdir) / "policy")
            policy = self._FakePolicy(b"policy-content")
            cache = WebSiteCache(base, "http://example", 1, "ua", fetch_policy=policy)

            cache._write_to_cache()

            self.assertTrue(Path(cache._cachename).exists())
            self.assertEqual(Path(cache._cachename).read_text(encoding="utf-8"), "policy-content")
            self.assertEqual(len(policy.calls), 1)
            self.assertEqual(policy.calls[0][0], "http://example")
            self.assertEqual(policy.calls[0][1], {"User-Agent": "ua"})

    def test_requests_http_fetch_policy_retries(self) -> None:
        policy = RequestsHttpFetchPolicy(timeout_seconds=0.5, retries=2)
        requests_exception = Exception("boom")

        ok_response = MagicMock()
        ok_response.raise_for_status.return_value = None
        ok_response.content = b"ok"

        with patch(
            "taren.websitecache.requests.get",
            side_effect=[requests_exception, ok_response],
        ) as get_mock:
            with patch("taren.websitecache.requests.RequestException", Exception):
                payload = policy.fetch("http://example", {"User-Agent": "ua"})

        self.assertEqual(payload, b"ok")
        self.assertEqual(get_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
