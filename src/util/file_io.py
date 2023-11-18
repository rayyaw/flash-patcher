import sys

from logging import exception
from pathlib import Path

from exception_handle.error_manager import ErrorManager


def read_safe(file_location: Path, error_manager: ErrorManager) -> str:
    """Read the full content from a file.
    
    Returns a string containing the entire file.
    """
    try:
        with Path.open(file_location) as file:
            return file.read()
    except (FileNotFoundError, IsADirectoryError):
        error_manager.context = file_location.as_posix()
        error_manager.raise_(
            """Invalid injection location.
            Could not find or load SWF decompiled file."""
        )

def readlines_safe(file_location: Path, error_manager: ErrorManager) -> list:
    """Read all lines from a file.
    
    Returns a list, with one entry for each line.
    """
    try:
        with Path.open(file_location) as file:
            return file.readlines()
    except (FileNotFoundError, IsADirectoryError):
        error_manager.context = file_location.as_posix()
        error_manager.raise_(
            """Invalid injection location.
            Could not find or load SWF decompiled file."""
        )

def writelines_safe(path: Path, lines: list) -> None:
    """Write a list of lines to a file."""
    try:
        with Path.open(path, "w") as file:
            file.writelines(lines)
    except (FileNotFoundError, IsADirectoryError):
        exception(
            """The provided decompilation is not in a writable location. 
            Please ensure you have write access in the current directory.""",
        )
        sys.exit(1)
