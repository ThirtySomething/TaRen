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
    # Program identity
    # ---------------------------------------------------------------------------
    PROGRAM_NAME: str = "TaRen"

    # ---------------------------------------------------------------------------
    # Collection subfolder names
    # ---------------------------------------------------------------------------
    FOLDER_DOWNLOADS: str = "downloads"
    FOLDER_SEEN: str = "seen"
    FOLDER_UNSEEN: str = "unseen"
    FOLDER_TRASH: str = ".trash"

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
    CFG_KEY_HTTP_TIMEOUT: str = "http_timeout"
    CFG_KEY_HTTP_RETRIES: str = "http_retries"
    CFG_KEY_PARALLEL_WORKERS: str = "parallel_workers"
    CFG_KEY_EPISODE_CACHE_DB: str = "episode_cache_db"

    # ---------------------------------------------------------------------------
    # Runtime defaults
    # ---------------------------------------------------------------------------
    DEFAULT_EPISODE_CACHE_DB: str = "episodes.sqlite3"

    # ---------------------------------------------------------------------------
    # Cache configuration
    # ---------------------------------------------------------------------------
    URL_HASH_LENGTH: int = 8  # Length of MD5 hash used in cache filename


# Exception hierarchy for TaRen
class TarenError(Exception):
    """Base exception for all TaRen errors."""

    pass


class NetworkError(TarenError):
    """Raised when a network operation fails."""

    pass


class FileSystemError(TarenError):
    """Raised when a file system operation fails."""

    pass


class ConfigurationError(TarenError):
    """Raised when configuration is invalid."""

    pass
