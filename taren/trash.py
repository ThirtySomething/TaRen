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
        self._trashfolder: str = os.path.join(self._basedir, self._trash)
        self._trashignorefile: str = os.path.join(self._trashfolder, self._trashignore)
        logging.debug("basedir [%s]", self._basedir)
        logging.debug("trash [%s]", self._trash)
        logging.debug("trashage [%s]", self._trashage)
        logging.debug("trashfolder [%s]", self._trashfolder)
        logging.debug("trashignore [%s]", self._trashignorefile)

    ############################################################################
    def cleanup(self) -> int:
        """
        Delete files from trah older than configured age
        """
        # Delete ignore file for media server
        if os.path.exists(self._trashignorefile):
            Helper.delete_file(self._trashignorefile)
        deleted: int = 0
        # Calculate maximum age
        maxage: float = time.time() - self._trashage * 86400
        logging.info(
            "Delete files older than [%s] days from trash [%s]",
            self._trashage,
            self._trashfolder,
        )
        # Loop over all in trash
        for filename in os.listdir(self._trashfolder):
            # Build FQN
            fname: str = os.path.join(self._trashfolder, filename)
            # Check only files
            if os.path.isfile(fname):
                # Check age of file
                if os.path.getmtime(fname) < maxage:
                    # Perform deletion
                    Helper.delete_file(fname)
                    logging.info("Delete file [%s]", filename)
                    deleted = deleted + 1
        # Create ignore file for media server
        Path(self._trashignorefile).touch()
        return deleted

    ############################################################################
    def init(self) -> bool:
        """
        Ensure existence of the trash folder and the trashignore marker file
        """
        if not Helper.ensure_directory(self._trashfolder):
            return False
        if not os.path.exists(self._trashignorefile):
            Path(self._trashignorefile).touch()
        return True

    ############################################################################
    def list(self) -> int:
        """
        List all files from trah
        """
        logging.info("List files from trash [%s]", self._trashfolder)
        today: datetime = datetime.today()
        filesintrash: int = 0
        # Loop over all in trash
        for filename in os.listdir(self._trashfolder):
            # Build FQN
            fname: str = os.path.join(self._trashfolder, filename)
            # Check only files
            if os.path.isfile(fname):
                # Ignore marker for media servers
                if fname == self._trashignorefile:
                    continue
                # List file
                file_mod_time: datetime = datetime.fromtimestamp(os.path.getmtime(fname))
                age: timedelta = today - file_mod_time
                logging.info("File [%s|%02d]", filename, age.days)
                filesintrash += 1
        return filesintrash

    ############################################################################
    def move(self, file: str) -> bool:
        """
        Move file to trash and modify file date to deletion timestamp
        """

        # Extract plain filename and extension from source file
        filenameWithPath, fileExtension = os.path.splitext(file)
        filenameRaw: str = os.path.basename(filenameWithPath)

        logging.debug("File [%s] splittet into [%s] and [%s]", file, filenameRaw, fileExtension)

        # Build search mask for variants
        searchmask: str = filenameRaw + "*" + fileExtension
        logging.debug("Searchmask [%s]", searchmask)

        # Search for existing variants
        dst: str = ""
        dstVariants: list[str] = fnmatch.filter(os.listdir(self._trashfolder), searchmask)
        if len(dstVariants) == 0:
            dst = os.path.join(self._trashfolder, (filenameRaw + fileExtension))
        else:
            dst = os.path.join(
                self._trashfolder,
                (filenameRaw + "_" + str(len(dstVariants)) + fileExtension),
            )

        # Move file to trash
        logging.debug("Move file [%s] to [%s]", file, dst)
        try:
            os.rename(file, dst)
            # Modify timestamp
            now: float = time.time()
            logging.debug("Set access/modified timestamp of [%s] to [%s]", dst, now)
            os.utime(dst, (now, now))
            return True
        except OSError as exc:
            logging.error("failed to move file [%s] to trash [%s]: %s", file, dst, exc)
            return False
