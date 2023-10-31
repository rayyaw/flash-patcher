from __future__ import annotations

from logging import exception

class InjectionErrorManager:
    """Handle exceptions thrown by Flash Patcher during the injection stage."""
    def __init__(
        self: InjectionErrorManager, 
        patch_file: str,
        line_no: int,
        extra_info: str | None
    ) -> None:
        self.patchFile = patch_file
        self.lineNo = line_no

        # extra info is usually the content of the offending line
        self.extraInfo = extra_info

    def throw(self: InjectionErrorManager, mesg: str) -> None:
        """Throw the specified error message with the given context."""
        exception(
            """InjectionError at %s, line %d
            Context: %s
            %s
            Aborting...""",
            self.patchFile, self.lineNo, self.extraInfo, mesg
        )
