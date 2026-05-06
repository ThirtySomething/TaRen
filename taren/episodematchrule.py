from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from taren.episode import Episode


class EpisodeMatchRule(Protocol):
    def try_match(self, filename: str, episode: "Episode") -> bool | None:
        """Return True/False when handled, else None to continue chain."""
