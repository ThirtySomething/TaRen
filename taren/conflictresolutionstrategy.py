from typing import Protocol

from taren.conflictresolutionresult import ConflictResolutionResult


class ConflictResolutionStrategy(Protocol):
    def resolve(self, old_fqn: str, new_fqn: str) -> ConflictResolutionResult:
        """Resolve rename conflicts and return follow-up actions."""
