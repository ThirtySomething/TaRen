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

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../vendor/MDO/MDO/"))

from MDO import MDO


class TarenConfig(MDO):
    """
    Contains dynamic settings of TaRen
    """

    ############################################################################
    def setup(self: object) -> bool:
        self.add("logging", "logfile", "program.log")
        self.add("logging", "loglevel", "info")
        self.add("logging", "logstring", "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s:%(funcName)s | %(message)s")
        self.add("taren", "downloads", "v:\\tatort")
        self.add("taren", "extension", "mp4")
        self.add("taren", "maxcache", "1")
        self.add("taren", "pattern", "Tatort")
        self.add("taren", "playlist", "v:\\tatort\\Tatort.html")
        self.add("taren", "teamlist", "Teams")
        self.add("taren", "trash", ".trash")
        self.add("taren", "trashage", "3")
        self.add("taren", "wiki", "https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen")
        self.add("taren", "wiki_team", "https://de.wikipedia.org/wiki/Liste_der_Tatort-Ermittler")
