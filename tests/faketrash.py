import os


class FakeTrash:
    def __init__(self, init_ok: bool = True) -> None:
        self._init_ok = init_ok
        self.moved: list[str] = []

    def init(self) -> bool:
        return self._init_ok

    def move(self, file_path: str) -> None:
        self.moved.append(os.path.basename(file_path))
        if os.path.exists(file_path):
            os.remove(file_path)

    def cleanup(self) -> int:
        return 0

    def list(self) -> int:
        return 0
