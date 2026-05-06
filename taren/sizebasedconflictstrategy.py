import logging
import os

from taren.conflictresolutionresult import ConflictResolutionResult


class SizeBasedConflictStrategy:
    """Default conflict strategy based on file size comparison."""

    def resolve(self, old_fqn: str, new_fqn: str) -> ConflictResolutionResult:
        if not os.path.exists(new_fqn):
            return ConflictResolutionResult(move_to_trash=None, skip_rename=False)

        size_old: int = os.stat(old_fqn).st_size
        size_new: int = os.stat(new_fqn).st_size

        if size_old == size_new:
            logging.info("file size equal, move file [%s] to trash", new_fqn)
            return ConflictResolutionResult(move_to_trash=new_fqn, skip_rename=False)

        if size_old > size_new:
            logging.info("one file smaller than the other one, move file [%s] to trash", new_fqn)
            return ConflictResolutionResult(move_to_trash=new_fqn, skip_rename=False)

        logging.info("one file smaller than the other one, move file [%s] to trash", old_fqn)
        return ConflictResolutionResult(move_to_trash=old_fqn, skip_rename=True)
