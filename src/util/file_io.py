import sys

from logging import exception
from pathlib import Path

from util.exception import InjectionErrorManager

def read_from_file(file_location: Path, error_manager: InjectionErrorManager) -> list:
    """Read all lines from a file.
    
    Returns a list, with one entry for each line.
    """
    try:
        with Path.open(file_location) as f:
            return f.readlines()
    except (FileNotFoundError, IsADirectoryError):
        error_manager.context = file_location.as_posix()
        error_manager.throw(
            """Invalid injection location.
            Could not find or load SWF decompiled file."""
        )

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