from __future__ import annotations

class DependencyError (Exception):
    """Exception raised for dependency-related errors."""

    def __init__(self: DependencyError, message: str) -> None:
        super().__init__(message)
