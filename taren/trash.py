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


class Trash:
    """
    Handling of trash bucket
    """

    ############################################################################
    def __init__(self: object, basedir: str, trash: str, trashage: int) -> None:
        """
        Default init of variables
        """
        self._basedir: str = basedir
        self._trash: str = trash
        self._trashage: int = trashage
        self._trashfolder: str = os.path.join(self._basedir, self._trash)
        logging.debug("basedir [{}]".format(self._basedir))
        logging.debug("trash [{}]".format(self._trash))
        logging.debug("trashfolder [{}]".format(self._trashfolder))
        logging.debug("trashage [{}]".format(self._trashage))

    ############################################################################
    def cleanup(self: object) -> int:
        """
        Delete files from trah older than configured age
        """
        deleted: int = 0
        # Calculate maximum age
        maxage: int = time.time() - self._trashage * 86400
        logging.info("Delete files older than [{}] days from trash [{}]".format(self._trashage, self._trashfolder))
        # Loop over all in trash
        for filename in os.listdir(self._trashfolder):
            # Build FQN
            fname: str = os.path.join(self._trashfolder, filename)
            # Check only files
            if os.path.isfile(fname):
                # Check age of file
                if os.path.getmtime(fname) < maxage:
                    # Perform deletion
                    os.remove(fname)
                    logging.info("Delete file [{}]".format(filename))
                    deleted = deleted + 1
        return deleted

    ############################################################################
    def init(self: object) -> bool:
        """
        Ensure existence of the trash folder
        """
        if not os.path.exists(self._trashfolder):
            try:
                # Create missing folder
                os.mkdir(self._trashfolder)
                logging.debug("Directory [{}] created".format(self._trashfolder))
            except OSError:
                logging.error("Creation of the directory [{}] failed, abort".format(self._trashfolder))
                return False
        else:
            logging.debug("Directory [{}] alread exists".format(self._trashfolder))
        return True

    ############################################################################
    def list(self: object) -> int:
        """
        List all files from trah
        """
        logging.info("List files from trash [{}]".format(self._trashfolder))
        filesintrash: int = 0
        # Loop over all in trash
        for filename in os.listdir(self._trashfolder):
            # Build FQN
            fname: str = os.path.join(self._trashfolder, filename)
            # Check only files
            if os.path.isfile(fname):
                # List file
                logging.info("File [{}]".format(filename))
                filesintrash += 1
        return filesintrash

    ############################################################################
    def move(self: object, file: str) -> None:
        """
        Move file to trash and modify file date to deletion timestamp
        """

        # Extract plain filename and extension from source file
        filenameWithPath, fileExtension = os.path.splitext(file)
        filenameRaw: str = os.path.basename(filenameWithPath)

        logging.debug("File [{}] splittet into [{}] and [{}]".format(file, filenameRaw, fileExtension))

        # Build search mask for variants
        searchmask: str = filenameRaw + "*" + fileExtension
        logging.debug("Searchmask [{}]".format(searchmask))

        # Search for existing variants
        dst: str = ""
        dstVariants: list[str] = fnmatch.filter(os.listdir(self._trashfolder), searchmask)
        if 0 == len(dstVariants):
            dst = os.path.join(self._trashfolder, (filenameRaw + fileExtension))
        else:
            dst = os.path.join(self._trashfolder, (filenameRaw + "_" + str(len(dstVariants)) + fileExtension))

        # Build destination name
        dst: str = os.path.join(self._trashfolder, dst)

        # Move file to trash
        logging.debug("Move file [{}] to [{}]".format(file, dst))
        os.rename(file, dst)
        # Modify timestamp
        now: float = time.time()
        logging.debug("Set access/modified timestamp of [{}] to [{}]".format(dst, now))
        os.utime(dst, (now, now))
