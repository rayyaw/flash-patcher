from __future__ import annotations

from flash_patcher.exception_handle.error_manager import ErrorManager

class InjectionLocation:
    """Store the location within a file to inject at.

    This will resolve a symbolic location (like "end") into a line number,
    which can then be injected.
    """

    line_no: int = None
    symbolic_location: str = None

    def __init__(self: InjectionLocation, symbolic_location: str) -> None:
        if symbolic_location.isdigit():
            # the -1 is required to ensure we're injecting in the right location
            self.line_no = int(symbolic_location) - 1

            # edge case of injecting at line 0
            self.line_no = max(self.line_no, 0)

        self.symbolic_location = symbolic_location

    def resolve(
        self: InjectionLocation,
        file_content: list[str],
        exception: ErrorManager
    ) -> int:
        """Resolve the injection location in the given file.
        
        If it was unable to resolve, use error_line_no to throw and exception.
        """
        if self.line_no is not None:
            # Injecting by line number
            return self.resolve_line_no(file_content, exception)

        if self.symbolic_location == "end":
            # Injecting at the end of a file
            return self.resolve_end(file_content)

        # Unknown injection location
        exception.context = self.symbolic_location
        exception.raise_(
            """Invalid add location.
            Expected keyword or integer (got type "str").""",
        )

    def resolve_line_no(
        self: InjectionLocation,
        file_content: list[str],
        exception: ErrorManager
    ) -> int:
        """Resolve the injection location if it's a line number."""
        if self.line_no > len(file_content):
            exception.raise_(
                f"""Out of bounds add location {self.symbolic_location}.
                The provided location is outside the maximum line number in the file."""
            )

        return self.line_no

    def resolve_end(
        self: InjectionLocation,
        file_content: list[str],
    ) -> int:
        """Resolve the injection location if it's the end of the file."""
        return len(file_content)
