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

from typing import Any


class Stats:
    """
    Statistic object, contains counter for
    - Episodes total
    - Episodes owned
    - Downloads deleted
    - Downloads in trash
    """

    ############################################################################
    def __init__(self) -> None:
        self.downloads_deleted: int = 0
        self.downloads_failed: int = 0
        self.downloads_moved: int = 0
        self.downloads_renamed: int = 0
        self.downloads_total: int = 0
        self.downloads_trash: int = 0
        self.episodes_owned: int = 0
        self.episodes_total: int = 0

    ############################################################################
    def __repr__(self):
        """Represent statistics as string"""
        return self.__str__()

    ############################################################################
    def to_dict(self) -> dict[str, Any]:
        """Convert statistics to dictionary format for JSON serialization"""
        owned_pct: float = (100.0 / self.episodes_total * self.episodes_owned) if self.episodes_total else 0.0
        return {
            "episodes_total": self.episodes_total,
            "episodes_owned": self.episodes_owned,
            "episodes_owned_percent": owned_pct,
            "downloads_total": self.downloads_total,
            "downloads_renamed": self.downloads_renamed,
            "downloads_moved": self.downloads_moved,
            "downloads_deleted": self.downloads_deleted,
            "downloads_failed": self.downloads_failed,
            "downloads_trash": self.downloads_trash,
        }

    ############################################################################
    def __str__(self):
        """Represent statistics as deterministic key-value format"""
        owned_pct: float = (100.0 / self.episodes_total * self.episodes_owned) if self.episodes_total else 0.0
        lines = [
            f"episodes_total: {self.episodes_total}",
            f"episodes_owned: {self.episodes_owned} ({owned_pct:.2f}%)",
            f"downloads_total: {self.downloads_total}",
            f"downloads_renamed: {self.downloads_renamed}",
            f"downloads_moved: {self.downloads_moved}",
            f"downloads_deleted: {self.downloads_deleted}",
            f"downloads_failed: {self.downloads_failed}",
            f"downloads_trash: {self.downloads_trash}",
        ]
        return "\n".join(lines)
