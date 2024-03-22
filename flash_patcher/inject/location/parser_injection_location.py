from __future__ import annotations

from flash_patcher.antlr_source.PatchfileParser import PatchfileParser

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.inject.location.injection_location import InjectionLocation

class ParserInjectionLocation (InjectionLocation):
    """Store the location within a file to inject at.

    This will resolve a symbolic location (like "end") into a line number,
    which can then be injected.

    This uses the parser context to find the correct location.
    """

    context: PatchfileParser.LocationTokenContext = None

    def __init__(
        self: ParserInjectionLocation,
        symbolic_location: PatchfileParser.LocationTokenContext
    ) -> None:
        self.context = symbolic_location

    def resolve(
        self: ParserInjectionLocation,
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

        elif isinstance(self.context, PatchfileParser.TextContext):
            line_no = self.resolve_text(file_content, exception)

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
        self: ParserInjectionLocation,
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
        self: ParserInjectionLocation,
        file_content: list[str],
        exception: ErrorManager,
    ) -> int | None:
        """Resolve the injection location if it's a function + offset."""
        line_no = None
        curly_brace_line = None
        found_fn = False

        for i, line in enumerate(file_content):
            # Do some replacement to ensure that function names are processed correctly
            line = line.replace("(", " ")
            line = line.replace(")", " ")

            if line.split()[:2] == ["function", self.context.TEXT_BLOCK().getText()] \
                or line.split()[:3] == [self.context.TEXT_BLOCK().getText(), "=", "function"]:
                # We need to add after the specified line
                line_no = i + 1
                found_fn = True

            # If there's no function offset, we want to inject after the {,
            # not the function name line
            if found_fn and '{' in line:
                curly_brace_line = i + 1
                break

        if line_no is not None:
            if self.context.INTEGER():
                line_no += int(self.context.INTEGER().getText())

            else:
                line_no = curly_brace_line

            self.verify_line_no(line_no, file_content, exception)

        return line_no

    def resolve_text(
        self: ParserInjectionLocation,
        file_content: list[str],
        exception: ErrorManager,
    ) -> int | None:
        """Resolve the injection location if it's content + offset.
        Will return the line of the last character of the content being matched.
        Will return None if there is no such content in the file.
        """
        matched_chars = 0
        search_query = self.context.replaceBlockText().getText().strip()

        # Since we need to match across multiple lines, we need to iterate through each character
        for i, line in enumerate(file_content):
            for char in line:
                matched_chars = self.update_matched_chars(
                    char, search_query[matched_chars], matched_chars
                )

                if matched_chars == len(search_query):
                    line_no = i + 1
                    if self.context.INTEGER():
                        line_no += int(self.context.INTEGER().getText())

                    self.verify_line_no(line_no, file_content, exception)
                    return line_no

            matched_chars = self.update_matched_chars(
                '\n', search_query[matched_chars], matched_chars
            )
            # No check if we've reached the end of the search query.
            # The strip() ensures the last character will never be a newline

        return None

    def resolve_end(
        self: ParserInjectionLocation,
        file_content: list[str],
    ) -> int:
        """Resolve the injection location if it's the end of the file."""
        return len(file_content)

    def verify_line_no(
        self: ParserInjectionLocation,
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

    def update_matched_chars(
        self: ParserInjectionLocation,
        first: str,
        second: str,
        num_matched: int,
    ) -> int:
        """Returns the new number of matched characters in a string,
        after comparing the two provided characters.
        """
        if first == second:
            return num_matched + 1

        return 0
