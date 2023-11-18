from __future__ import annotations

import sys
from logging import error, exception

from exception_handle.injection import InjectionError

class ErrorManager:
    """Handle exceptions thrown by Flash Patcher during the injection stage."""
    patch_file: str
    line_no: int
    context: str

    def __init__(
        self: ErrorManager,
        patch_file: str,
        line_no: int,
        context: str | None = None,
    ) -> None:
        self.patch_file = patch_file
        self.line_no = line_no

        # extra info is usually the content of the offending line
        self.context = context

    def throw(self: ErrorManager, mesg: str) -> None:
        """Throw the specified error message with the given context."""
        exception(
            """InjectionError at %s, line %d
            Context: %s
            %s
            Aborting...""",
            self.patch_file, self.line_no, self.context, mesg
        )
        sys.exit(1)

    def raise_(self: ErrorManager, mesg: str) -> None:
        """Throw the specified error message with the given context."""
        error_mesg = f"""InjectionError at {self.patch_file}, line {self.line_no}
            Additional context: {self.context}
            {mesg}
            Aborting..."""

        error(error_mesg)
        raise InjectionError(mesg)
