from __future__ import annotations

class InjectionError (Exception):
    """Exception raised for dependency-related errors."""

    def __init__(self: InjectionError, message: str) -> None:
        super().__init__(message)
