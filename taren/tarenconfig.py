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


def _load_mdo_class() -> type:
    try:
        return import_module("MDO").MDO
    except ModuleNotFoundError:
        vendor_mdo_path: Path = (
            Path(__file__).resolve().parent.parent / "vendor" / "MDO" / "MDO"
        )
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
        self.add("logging", "logfile", "program.log")
        self.add("logging", "loglevel", "info")
        self.add(
            "logging",
            "logstring",
            "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s:%(funcName)s | %(message)s",
        )
        self.add("taren", "downloads", "v:\\tatort")
        self.add("taren", "extension", "mp4")
        self.add("taren", "maxcache", "6")
        self.add("taren", "pattern", "Tatort")
        self.add("taren", "trash", ".trash")
        self.add("taren", "trashage", "3")
        self.add("taren", "trashignore", ".ignore")
        self.add(
            "taren", "wiki", "https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen"
        )
        self.add(
            "taren",
            "wiki_useragent",
            "TaRen/0.0 (https://github.com/ThirtySomething/TaRen/) generic-library/0.0",
        )
        return True
