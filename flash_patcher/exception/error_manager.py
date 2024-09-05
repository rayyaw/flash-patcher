from __future__ import annotations

from flash_patcher.exception.injection import InjectionError
from flash_patcher.util.logging import logger

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

    def raise_(
        self: ErrorManager,
        mesg: str,
        exc_type: type[Exception] = InjectionError
    ) -> None:
        """Raise an error with the requested information."""
        error_mesg = f"""{exc_type.__name__} at {self.patch_file}, line {self.line_no}
            Additional context: {self.context}
            {mesg}
            Aborting..."""

        logger.error(error_mesg)
        raise exc_type(mesg)
