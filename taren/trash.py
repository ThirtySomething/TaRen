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

import fnmatch
import logging
import os
import time
from datetime import datetime, timedelta

from pathlib import Path

from taren.helper import Helper
from taren.tarendefines import FileSystemError

logger = logging.getLogger(__name__)


class Trash:
    """
    Handling of trash bucket
    """

    ############################################################################
    def __init__(self, basedir: str, trash: str, trashage: int, trashignore: str) -> None:
        """
        Default init of variables
        """
        self._basedir: str = basedir
        self._trash: str = trash
        self._trashage: int = trashage
        self._trashignore: str = trashignore
        self._trashfolder_path: Path = Path(self._basedir) / self._trash
        self._trashignorefile_path: Path = self._trashfolder_path / self._trashignore
        self._trashfolder: str = str(self._trashfolder_path)
        self._trashignorefile: str = str(self._trashignorefile_path)
        logger.debug("basedir [%s]", self._basedir)
        logger.debug("trash [%s]", self._trash)
        logger.debug("trashage [%s]", self._trashage)
        logger.debug("trashfolder [%s]", self._trashfolder)
        logger.debug("trashignore [%s]", self._trashignorefile)

    ############################################################################
    def cleanup(self) -> int:
        """
        Delete files from trah older than configured age
        """
        # Delete ignore file for media server
        if self._trashignorefile_path.exists():
            Helper.delete_file(self._trashignorefile)
        deleted: int = 0
        # Calculate maximum age
        maxage: float = time.time() - self._trashage * 86400
        logger.info(
            "Delete files older than [%s] days from trash [%s]",
            self._trashage,
            self._trashfolder,
        )
        # Loop over all in trash
        for trash_file in self._trashfolder_path.iterdir():
            filename: str = trash_file.name
            # Check only files
            if trash_file.is_file():
                # Check age of file
                if trash_file.stat().st_mtime < maxage:
                    # Perform deletion
                    Helper.delete_file(str(trash_file))
                    logger.info("Delete file [%s]", filename)
                    deleted = deleted + 1
        # Create ignore file for media server
        self._trashignorefile_path.touch()
        return deleted

    ############################################################################
    def init(self) -> None:
        """
        Ensure existence of the trash folder and the trashignore marker file

        Raises FileSystemError if the trash directory cannot be created.
        """
        if not Helper.ensure_directory(str(self._trashfolder_path)):
            raise FileSystemError(f"Failed to create trash directory: {self._trashfolder}")
        if not self._trashignorefile_path.exists():
            self._trashignorefile_path.touch()

    ############################################################################
    def list(self) -> int:
        """
        List all files from trah
        """
        logger.info("List files from trash [%s]", self._trashfolder)
        today: datetime = datetime.today()
        filesintrash: int = 0
        # Loop over all in trash
        for trash_file in self._trashfolder_path.iterdir():
            filename: str = trash_file.name
            # Check only files
            if trash_file.is_file():
                # Ignore marker for media servers
                if trash_file == self._trashignorefile_path:
                    continue
                # List file
                file_mod_time: datetime = datetime.fromtimestamp(trash_file.stat().st_mtime)
                age: timedelta = today - file_mod_time
                logger.info("File [%s|%02d]", filename, age.days)
                filesintrash += 1
        return filesintrash

    ############################################################################
    def move(self, file: str) -> bool:
        """
        Move file to trash and modify file date to deletion timestamp
        """

        # Extract plain filename and extension from source file
        file_path: Path = Path(file)
        filename_raw: str = file_path.stem
        file_extension: str = file_path.suffix

        logger.debug("File [%s] splittet into [%s] and [%s]", file, filename_raw, file_extension)

        # Build search mask for variants
        searchmask: str = f"{filename_raw}*{file_extension}"
        logger.debug("Searchmask [%s]", searchmask)

        # Search for existing variants
        dst_variants: list[str] = fnmatch.filter(os.listdir(self._trashfolder), searchmask)
        counter: int = len(dst_variants) + 1
        dst_path: Path = self._trashfolder_path / f"{filename_raw}_{counter:02d}{file_extension}"
        # Guard against races: another thread may have claimed this slot already
        while dst_path.exists():
            counter += 1
            dst_path = self._trashfolder_path / f"{filename_raw}_{counter:02d}{file_extension}"

        # Move file to trash
        logger.debug("Move file [%s] to [%s]", file, dst_path)
        try:
            os.rename(file, str(dst_path))
            # Modify timestamp
            now: float = time.time()
            logger.debug("Set access/modified timestamp of [%s] to [%s]", dst_path, now)
            os.utime(dst_path, (now, now))
            return True
        except OSError as exc:
            logger.error("failed to move file [%s] to trash [%s]: %s", file, dst_path, exc)
            return False
