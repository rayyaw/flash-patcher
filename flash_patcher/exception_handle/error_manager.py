from __future__ import annotations

from logging import error

from flash_patcher.exception_handle.injection import InjectionError

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

    def raise_(self: ErrorManager, mesg: str) -> None:
        """Raise an InjectionError with the requested information."""
        error_mesg = f"""InjectionError at {self.patch_file}, line {self.line_no}
            Additional context: {self.context}
            {mesg}
            Aborting..."""

        error(error_mesg)
        raise InjectionError(mesg)
