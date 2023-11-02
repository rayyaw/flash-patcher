from __future__ import annotations

from util.exception import ErrorManager

class InjectionLocation:
    """Store the location within a file to inject at.

    This will resolve a symbolic location (like "end") into a line number,
    which can then be injected.
    """

    lineNo: int = None
    symbolicLocation: str = None

    def __init__(self: InjectionLocation, symbolic_location: str) -> None:
        if symbolic_location.isdigit():
            # the -1 is required to ensure we're injecting in the right location
            self.lineNo = int(symbolic_location) - 1
        
        self.symbolicLocation = symbolic_location

    def resolve(
        self: InjectionLocation,
        file_content: list,
        exception: ErrorManager
    ) -> int:
        """Resolve the injection location in the given file.
        
        If it was unable to resolve, use error_line_no to throw and exception.
        """
        if self.lineNo is not None:
            # Injecting by line number
            return self.resolve_line_no(file_content, exception)
        
        elif self.symbolicLocation == "end":
            # Injecting at the end of a file
            return self.resolve_end(file_content, exception)
        
        else:
            # Unknown injection location
            exception(
                """%s, line %d: Invalid add location.
                Expected keyword or integer (got type "str").""",
                self.symbolicLocation,
                exception,
            )

    def resolve_line_no(
        self: InjectionLocation,
        file_content: list,
        exception: ErrorManager
    ) -> int:
        if self.lineNo > len(file_content):
            exception.throw(
                """Out of bounds add location.
                The provided location is outside the maximum line number in the file."""
            )

        return self.lineNo
    
    def resolve_end(
        self: InjectionLocation,
        file_content: list,
        exception: ErrorManager
    ) -> int:
        return len(file_content)