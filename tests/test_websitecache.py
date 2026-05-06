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

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from fakepolicy import FakePolicy
from taren.helper import Helper
from taren.requestshttpfetchpolicy import RequestsHttpFetchPolicy
from taren.websitecache import WebSiteCache


class TestWebsiteCache(unittest.TestCase):
    def test_write_to_cache_success_and_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = str(Path(tmpdir) / "cache")
            cache = WebSiteCache(base, "http://example", 1, "ua")

            response = MagicMock()
            response.content = b"<html>ok</html>"
            response.raise_for_status.return_value = None

            with patch("taren.requestshttpfetchpolicy.requests.get", return_value=response):
                cache._write_to_cache()
            self.assertTrue(Path(cache._cachename).exists())

            failed = WebSiteCache(str(Path(tmpdir) / "cache_fail"), "http://example", 1, "ua")
            with patch(
                "taren.requestshttpfetchpolicy.requests.get",
                side_effect=Exception("boom"),
            ):
                with patch("taren.requestshttpfetchpolicy.requests.RequestException", Exception):
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
                patch("taren.requestshttpfetchpolicy.requests.get", return_value=response),
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
            policy = FakePolicy(b"policy-content")
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
            "taren.requestshttpfetchpolicy.requests.get",
            side_effect=[requests_exception, ok_response],
        ) as get_mock:
            with patch("taren.requestshttpfetchpolicy.requests.RequestException", Exception):
                payload = policy.fetch("http://example", {"User-Agent": "ua"})

        self.assertEqual(payload, b"ok")
        self.assertEqual(get_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
