import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from taren.helper import Helper
from taren.websitecache import WebSiteCache


class TestWebsiteCache(unittest.TestCase):
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

            failed = WebSiteCache(
                str(Path(tmpdir) / "cache_fail"), "http://example", 1, "ua"
            )
            with patch(
                "taren.websitecache.requests.get", side_effect=Exception("boom")
            ):
                with patch("taren.websitecache.requests.RequestException", Exception):
                    failed._write_to_cache()
            self.assertFalse(Path(failed._cachename).exists())

    def test_get_website_from_cache_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = str(Path(tmpdir) / "cache")
            cache = WebSiteCache(base, "http://example", 1, "ua")

            Path(cache._cachename).write_text("cached", encoding="utf-8")
            self.assertEqual(cache.get_website_from_cache(), "cached")

            missing = WebSiteCache(
                str(Path(tmpdir) / "missing"), "http://example", 1, "ua"
            )
            with patch.object(WebSiteCache, "_write_to_cache", return_value=None):
                self.assertEqual(missing.get_website_from_cache(), "")

    def test_get_website_from_cache_deletes_stale_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = str(Path(tmpdir) / "stale")
            cache = WebSiteCache(base, "http://example", 1, "ua")
            Path(cache._cachename).write_text("stale", encoding="utf-8")

            with (
                patch.object(WebSiteCache, "_get_age_in_days", return_value=10),
                patch(
                    "taren.websitecache.Helper.delete_file", wraps=Helper.delete_file
                ),
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


if __name__ == "__main__":
    unittest.main()
