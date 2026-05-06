import logging
import os

from taren.stats import Stats


class RenameFileCommand:
    def __init__(self, source_file: str, destination_file: str) -> None:
        self._source_file: str = source_file
        self._destination_file: str = destination_file

    def execute(self, statistics: Stats) -> None:
        logging.info(
            "rename from [%s] to [%s] filename",
            self._source_file,
            self._destination_file,
        )
        os.rename(self._source_file, self._destination_file)
        statistics.downloads_renamed += 1
