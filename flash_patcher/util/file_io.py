from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Type

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.util.logging import logger

class FileWritebackManager:
    """Handle files. Will open and read the content, and writeback when the file is closed."""

    file_location: Path
    error_manager: ErrorManager

    # If set to true, return a list of lines instead of the file as a string
    readlines: bool

    content: str | list[str]

    def __init__(
        self: FileWritebackManager,
        file_location: Path,
        error_manager: ErrorManager,
        readlines: bool = False,
    ) -> None:
        self.file_location = file_location
        self.error_manager = error_manager

        self.readlines = readlines

    def __enter__(self: FileWritebackManager) -> str | list[str]:
        if self.readlines:
            self.content = readlines_safe(self.file_location, self.error_manager)
        else:
            self.content = read_safe(self.file_location, self.error_manager)

        return self.content

    def __exit__(
        self: FileWritebackManager,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        if isinstance(self.content, str):
            self.content = [self.content]

        writelines_safe(self.file_location, self.content)

def read_safe(file_location: Path, error_manager: ErrorManager) -> str:
    """Read the full content from a file.
    
    Returns a string containing the entire file.
    """
    try:
        with file_location.open() as file:
            return file.read()
    except (FileNotFoundError, IsADirectoryError) as exc:
        error_manager.context = file_location.as_posix()
        error_manager.raise_(
            """Invalid injection location.
            Could not find or load SWF decompiled file.""",
            type(exc)
        )

def readlines_safe(file_location: Path, error_manager: ErrorManager) -> list:
    """Read all lines from a file.
    
    Returns a list, with one entry for each line.
    """
    try:
        with file_location.open() as file:
            return file.readlines()
    except (FileNotFoundError, IsADirectoryError) as exc:
        error_manager.context = file_location.as_posix()
        error_manager.raise_(
            """Invalid injection location.
            Could not find or load SWF decompiled file.""",
            type(exc)
        )

def writelines_safe(path: Path, lines: list[str]) -> None:
    """Write a list of lines to a file."""
    try:
        with path.open("w") as file:
            file.writelines(lines)
    except (FileNotFoundError, IsADirectoryError) as exc:
        mesg = """The provided decompilation is not in a writable location.
            Please ensure you have write access in the current directory."""
        logger.exception(mesg)
        raise exc
