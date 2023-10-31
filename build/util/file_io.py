import sys

from logging import exception
from pathlib import Path

def read_from_file(file_location: Path, patch_file: Path, current_line_no: int) -> list:
    """
    Read all lines from a file.
    Returns a list, with one entry for each line.
    """
    try:
        with Path.open(file_location) as f:
            return f.readlines()
    except (FileNotFoundError, IsADirectoryError):
        exception(
            """%s, line %d: Invalid injection location.
            Could not find or load SWF decompiled file at: %s
            Aborting...""",
            patch_file,
            current_line_no,
            file_location,
        )
        sys.exit(1)

def write_to_file(path: Path, lines: list) -> None:
    """Write a list of lines to a file."""
    try:
        with Path.open(path, "w") as f:
            f.writelines(lines)
    except (FileNotFoundError, IsADirectoryError):
        exception(
            """The provided decompilation is not in a writable location. 
            Please ensure you have write access in the current directory.""",
        )
        sys.exit(1)