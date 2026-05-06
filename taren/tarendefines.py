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


class TarenDefines:
    """Centralised text constants for TaRen."""

    # ---------------------------------------------------------------------------
    # Collection subfolder names
    # ---------------------------------------------------------------------------
    FOLDER_DOWNLOADS: str = "downloads"
    FOLDER_SEEN: str = "seen"
    FOLDER_TRASH: str = "trash"

    # ---------------------------------------------------------------------------
    # Configuration section names
    # ---------------------------------------------------------------------------
    CFG_SECTION_LOGGING: str = "logging"
    CFG_SECTION_TAREN: str = "taren"

    # ---------------------------------------------------------------------------
    # Configuration key names — logging section
    # ---------------------------------------------------------------------------
    CFG_KEY_LOGFILE: str = "logfile"
    CFG_KEY_LOGLEVEL: str = "loglevel"
    CFG_KEY_LOGSTRING: str = "logstring"

    # ---------------------------------------------------------------------------
    # Configuration key names — taren section
    # ---------------------------------------------------------------------------
    CFG_KEY_COLLECTION: str = "collection"
    CFG_KEY_EXTENSION: str = "extension"
    CFG_KEY_MAXCACHE: str = "maxcache"
    CFG_KEY_PATTERN: str = "pattern"
    CFG_KEY_TRASHAGE: str = "trashage"
    CFG_KEY_TRASHIGNORE: str = "trashignore"
    CFG_KEY_WIKI: str = "wiki"
    CFG_KEY_WIKI_USERAGENT: str = "wiki_useragent"
