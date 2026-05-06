from taren.stats import Stats
from taren.trash import Trash


class MoveToTrashCommand:
    def __init__(self, trash: Trash, file_path: str) -> None:
        self._trash: Trash = trash
        self._file_path: str = file_path

    def execute(self, statistics: Stats) -> None:
        self._trash.move(self._file_path)
        statistics.downloads_moved += 1
