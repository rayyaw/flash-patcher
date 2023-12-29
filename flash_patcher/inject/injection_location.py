from __future__ import annotations

from flash_patcher.antlr_source.PatchfileParser import PatchfileParser

from flash_patcher.exception.error_manager import ErrorManager

class InjectionLocation:
    """Store the location within a file to inject at.

    This will resolve a symbolic location (like "end") into a line number,
    which can then be injected.
    """

    context: PatchfileParser.LocationTokenContext = None

    def __init__(
        self: InjectionLocation,
        symbolic_location: PatchfileParser.LocationTokenContext
    ) -> None:
        self.context = symbolic_location

    def resolve(
        self: InjectionLocation,
        file_content: list[str],
        is_add: bool,
        exception: ErrorManager,
    ) -> int | None:
        """Resolve the injection location in the given file, or None if none exists.
        
        If it was unable to resolve, use error_line_no to throw and exception.
        """
        line_no = None
        if isinstance(self.context, PatchfileParser.LineNumberContext):
            line_no = self.resolve_line_no(file_content, is_add, exception)

        elif isinstance(self.context, PatchfileParser.FunctionContext):
            line_no = self.resolve_function(file_content, exception)

        elif isinstance(self.context, PatchfileParser.EndContext):
            line_no = self.resolve_end(file_content)

        # Unknown injection location
        else:
            exception.context = self.context
            exception.raise_(
                f"""Invalid file location.
                Expected keyword or integer (got type "{type(self.context)}").""",
            )

        if line_no is None:
            return line_no

        return max(line_no, 0)

    def resolve_line_no(
        self: InjectionLocation,
        file_content: list[str],
        is_add: bool,
        exception: ErrorManager
    ) -> int:
        """Resolve the injection location if it's a line number."""
        line_no = int(self.context.INTEGER().getText())

        # ensure we inject before the line
        if is_add:
            line_no -= 1

        self.verify_line_no(line_no, file_content, exception)

        return line_no

    def resolve_function(
        self: InjectionLocation,
        file_content: list[str],
        exception: ErrorManager,
    ) -> int | None:
        """Resolve the injection location if it's a function + offset."""
        line_no = None
        for i, line in enumerate(file_content):
            # Do some replacement to ensure that function names are processed correctly
            line = line.replace("(", " ")
            line = line.replace(")", " ")

            if line.split()[:2] == ["function", self.context.FUNCTION_NAME().getText()] \
                or line.split()[:3] == [self.context.FUNCTION_NAME().getText(), "=", "function"]:
                # We need to add after the specified line
                line_no = i + 1
                break

        if line_no is not None:
            if self.context.INTEGER():
                line_no += int(self.context.INTEGER().getText())

            self.verify_line_no(line_no, file_content, exception)

        return line_no

    def resolve_end(
        self: InjectionLocation,
        file_content: list[str],
    ) -> int:
        """Resolve the injection location if it's the end of the file."""
        return len(file_content)

    def verify_line_no(
        self: InjectionLocation,
        line_no: int,
        file_content: list[str],
        exception: ErrorManager,
    ) -> None:
        """Verify that the line number is not beyond EOF, and throw an exception if it is."""
        if line_no > len(file_content):
            exception.raise_(
                f"""Out of bounds file location {line_no}.
                The provided location is outside the maximum line number in the file."""
            )
