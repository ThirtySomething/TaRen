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
    Statistic object, contains collection-based counters for
    - Downloads count
    - Seen count and percentage
    - Unseen count and percentage
    - Trash count
    - Episodes total and owned
    """

    ############################################################################
    def __init__(self) -> None:
        # Collection counts (after processing)
        self.collection_downloads: int = 0
        self.collection_seen: int = 0
        self.collection_unseen: int = 0
        self.collection_trash: int = 0
        # Episode counts
        self.episodes_total: int = 0
        self.episodes_owned: int = 0

    ############################################################################
    def _calculate_episodes_owned_percentage(self) -> float:
        """Calculate episodes owned as percentage of total"""
        return (100.0 / self.episodes_total * self.episodes_owned) if self.episodes_total else 0.0

    ############################################################################
    def _calculate_seen_percentage(self) -> float:
        """Calculate seen items as percentage of episodes owned (seen / episodes_owned)."""
        return (100.0 / self.episodes_owned * self.collection_seen) if self.episodes_owned else 0.0

    ############################################################################
    def _calculate_unseen_percentage(self) -> float:
        """Calculate unseen items as percentage of episodes owned (unseen / episodes_owned)."""
        return (100.0 / self.episodes_owned * self.collection_unseen) if self.episodes_owned else 0.0

    ############################################################################
    def _calculate_trash_percentage(self) -> float:
        """Deprecated: trash percentage is not used in reporting; kept for compatibility."""
        return 0.0

    ############################################################################
    def update_episodes_owned_from_collection(self) -> None:
        """
        Update episodes_owned to be the sum of collection_seen and collection_unseen.
        This ensures that episodes_owned represents all episodes actually in the collection.
        """
        self.episodes_owned = self.collection_seen + self.collection_unseen

    ############################################################################
    def to_dict(self) -> dict[str, Any]:
        """Convert statistics to dictionary format for JSON serialization"""
        episodes_owned_pct: float = self._calculate_episodes_owned_percentage()
        seen_pct: float = self._calculate_seen_percentage()
        unseen_pct: float = self._calculate_unseen_percentage()

        return {
            "collection": {
                "downloads": self.collection_downloads,
                "seen": self.collection_seen,
                "unseen": self.collection_unseen,
                "trash": self.collection_trash,
            },
            "episodes": {
                "total": self.episodes_total,
                "owned": self.episodes_owned,
                "seen_percent": seen_pct,
                "unseen_percent": unseen_pct,
                "owned_percent": episodes_owned_pct,
            },
        }

    ############################################################################
    def __str__(self):
        """Represent statistics as deterministic key-value format focused on collection state"""
        episodes_owned_pct: float = self._calculate_episodes_owned_percentage()
        seen_pct: float = self._calculate_seen_percentage()
        unseen_pct: float = self._calculate_unseen_percentage()

        lines = [
            "=== COLLECTION STATUS ===",
            f"downloads: {self.collection_downloads}",
            f"seen: {self.collection_seen} ({seen_pct:.2f}%)",
            f"unseen: {self.collection_unseen} ({unseen_pct:.2f}%)",
            f"trash: {self.collection_trash}",
            "=== EPISODES STATUS ===",
            f"episodes_total: {self.episodes_total}",
            f"episodes_owned: {self.episodes_owned} ({episodes_owned_pct:.2f}%)",
        ]
        return "\n".join(lines)
