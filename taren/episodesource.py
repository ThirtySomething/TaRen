from typing import Protocol


class EpisodeSource(Protocol):
    def fetch(self) -> str:
        """Retrieve raw episode source content."""
