import sys

from logging import exception
from pathlib import Path
from typing import Callable

from util.exception import ErrorManager


def read_safe(file_location: Path, error_manager: ErrorManager) -> str:
    """Read the full content from a file.
    
    Returns a string containing the entire file.
    """
    try:
        with Path.open(file_location) as f:
            return f.read()
    except (FileNotFoundError, IsADirectoryError):
        error_manager.context = file_location.as_posix()
        error_manager.throw(
            """Invalid injection location.
            Could not find or load SWF decompiled file."""
        )

def readlines_safe(file_location: Path, error_manager: ErrorManager) -> list:
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

def writelines_safe(path: Path, lines: list) -> None:
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