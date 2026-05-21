import hashlib
from pathlib import Path


class FileFingerprint:
    """Compute SHA-1 fingerprint from size + head + tail chunks."""

    CHUNK_SIZE: int = 65536

    @staticmethod
    def compute(file_path: Path) -> str:
        """Return SHA-1 hex digest for file content signature."""
        hasher = hashlib.sha1()
        size = file_path.stat().st_size
        hasher.update(str(size).encode("utf-8"))
        with file_path.open("rb") as handle:
            head = handle.read(FileFingerprint.CHUNK_SIZE)
            hasher.update(head)
            if size > FileFingerprint.CHUNK_SIZE:
                handle.seek(max(0, size - FileFingerprint.CHUNK_SIZE))
                tail = handle.read(FileFingerprint.CHUNK_SIZE)
                hasher.update(tail)
        return hasher.hexdigest()
