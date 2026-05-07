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

import os
import sys
from importlib import import_module
from pathlib import Path
from urllib.parse import urlparse

from taren.tarendefines import TarenDefines


def _load_mdo_class() -> type:
    try:
        return import_module("MDO").MDO
    except ModuleNotFoundError:
        vendor_mdo_path: Path = Path(__file__).resolve().parent.parent / "vendor" / "MDO" / "MDO"
        vendor_mdo_path_str: str = str(vendor_mdo_path)
        if vendor_mdo_path.exists() and vendor_mdo_path_str not in sys.path:
            sys.path.insert(0, vendor_mdo_path_str)
        return import_module("MDO").MDO


MDO = _load_mdo_class()


class TarenConfig(MDO):
    """
    Contains dynamic settings of TaRen
    """

    ############################################################################
    def setup(self) -> bool:
        logfile_name: str = f"{TarenDefines.PROGRAM_NAME}.log"
        self.add(
            TarenDefines.CFG_SECTION_LOGGING,
            TarenDefines.CFG_KEY_LOGFILE,
            logfile_name,
        )
        self.add(TarenDefines.CFG_SECTION_LOGGING, TarenDefines.CFG_KEY_LOGLEVEL, "info")
        self.add(
            TarenDefines.CFG_SECTION_LOGGING,
            TarenDefines.CFG_KEY_LOGSTRING,
            "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s:%(funcName)s | %(message)s",
        )
        self.add(
            TarenDefines.CFG_SECTION_TAREN,
            TarenDefines.CFG_KEY_COLLECTION,
            "v:\\tatort",
        )
        self.add(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_EXTENSION, "mp4")
        self.add(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_MAXCACHE, "6")
        self.add(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_PATTERN, "Tatort")
        self.add(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_TRASHAGE, "3")
        self.add(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_TRASHIGNORE, ".ignore")
        self.add(
            TarenDefines.CFG_SECTION_TAREN,
            TarenDefines.CFG_KEY_WIKI,
            "https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen",
        )
        self.add(
            TarenDefines.CFG_SECTION_TAREN,
            TarenDefines.CFG_KEY_WIKI_USERAGENT,
            "TaRen/0.0 (https://github.com/ThirtySomething/TaRen/) generic-library/0.0",
        )
        self.add(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_HTTP_TIMEOUT, "10")
        self.add(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_HTTP_RETRIES, "1")
        return True

    ############################################################################
    def validate(self) -> list[str]:
        """Validate loaded configuration values and return a list of errors."""

        errors: list[str] = []

        def _require_text(section: str, key: str, label: str) -> str:
            value = self.value_get(section, key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label} must be a non-empty string")
                return ""
            return value.strip()

        def _require_int(
            section: str,
            key: str,
            label: str,
            min_value: int,
            max_value: int | None = None,
        ) -> int | None:
            raw_value: str = _require_text(section, key, label)
            if not raw_value:
                return None
            try:
                parsed_value: int = int(raw_value)
            except ValueError:
                errors.append(f"{label} must be an integer")
                return None
            if parsed_value < min_value:
                errors.append(f"{label} must be >= {min_value}")
                return None
            if max_value is not None and parsed_value > max_value:
                errors.append(f"{label} must be <= {max_value}")
                return None
            return parsed_value

        loglevel_allowed: set[str] = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}

        collection: str = _require_text(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_COLLECTION, "taren.collection")
        _require_text(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_EXTENSION, "taren.extension")
        _require_int(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_MAXCACHE, "taren.maxcache", 1)
        _require_text(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_PATTERN, "taren.pattern")
        _require_int(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_TRASHAGE, "taren.trashage", 0)
        _require_text(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_TRASHIGNORE, "taren.trashignore")
        wiki_url: str = _require_text(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_WIKI, "taren.wiki")
        _require_text(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_WIKI_USERAGENT, "taren.wiki_useragent")
        _require_int(TarenDefines.CFG_SECTION_TAREN, TarenDefines.CFG_KEY_HTTP_TIMEOUT, "taren.http_timeout", 1)
        _require_int(
            TarenDefines.CFG_SECTION_TAREN,
            TarenDefines.CFG_KEY_HTTP_RETRIES,
            "taren.http_retries",
            1,
            max_value=10,
        )

        logfile: str = _require_text(TarenDefines.CFG_SECTION_LOGGING, TarenDefines.CFG_KEY_LOGFILE, "logging.logfile")
        loglevel: str = _require_text(TarenDefines.CFG_SECTION_LOGGING, TarenDefines.CFG_KEY_LOGLEVEL, "logging.loglevel")
        _require_text(TarenDefines.CFG_SECTION_LOGGING, TarenDefines.CFG_KEY_LOGSTRING, "logging.logstring")

        if collection and not os.path.isdir(collection):
            errors.append(f"taren.collection does not exist or is not a directory: {collection}")

        if wiki_url:
            parsed_url = urlparse(wiki_url)
            if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
                errors.append(f"taren.wiki must be a valid http(s) URL: {wiki_url}")

        if loglevel and loglevel.upper() not in loglevel_allowed:
            errors.append(f"logging.loglevel must be one of: {', '.join(sorted(loglevel_allowed))}")

        if logfile and os.path.basename(logfile) != logfile:
            errors.append("logging.logfile must be a filename without path")

        return errors
