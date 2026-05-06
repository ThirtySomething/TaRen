from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from taren.stats import Stats


class FileMutationCommand(Protocol):
    def execute(self, statistics: "Stats") -> None:
        """Execute mutation and update statistics."""
