from __future__ import annotations

from abc import ABC, abstractmethod

from flash_patcher.exception.error_manager import ErrorManager

class InjectionLocation (ABC):
    """Store the location within a file to inject at.

    This will resolve into a line number, which can then be injected.
    """

    @abstractmethod
    def resolve(
        self: InjectionLocation,
        file_content: list[str],
        is_add: bool,
        exception: ErrorManager,
    ) -> int | None:
        """Resolve the injection location in the given file, or None if none exists.
        
        If it was unable to resolve, use error_line_no to throw and exception.
        """
        return None
