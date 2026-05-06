from typing import NamedTuple


class ConflictResolutionResult(NamedTuple):
    move_to_trash: str | None
    skip_rename: bool
