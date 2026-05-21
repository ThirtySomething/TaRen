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
