from __future__ import annotations

import sys
from logging import exception

class InjectionErrorManager:
    """Handle exceptions thrown by Flash Patcher during the injection stage."""
    patchFile: str
    lineNo: int
    context: str

    def __init__(
        self: InjectionErrorManager, 
        patch_file: str,
        line_no: int,
        context: str | None = None,
    ) -> None:
        self.patchFile = patch_file
        self.lineNo = line_no

        # extra info is usually the content of the offending line
        self.context = context

    def throw(self: InjectionErrorManager, mesg: str) -> None:
        """Throw the specified error message with the given context."""
        exception(
            """InjectionError at %s, line %d
            Context: %s
            %s
            Aborting...""",
            self.patchFile, self.lineNo, self.context, mesg
        )
        sys.exit(1)