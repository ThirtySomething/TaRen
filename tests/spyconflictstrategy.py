from types import SimpleNamespace


class SpyConflictStrategy:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def resolve(self, old_fqn: str, new_fqn: str):
        self.calls.append((old_fqn, new_fqn))
        return SimpleNamespace(move_to_trash=None, skip_rename=False)
