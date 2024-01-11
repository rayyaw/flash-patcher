from __future__ import annotations

from pathlib import Path


from flash_patcher.antlr_source.PatchfileParser import PatchfileParser

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.inject.find.last_find_content import LastFindContentManager
from flash_patcher.inject.find.parser_find_content import ParserFindContentManager
from flash_patcher.inject.single_injection import SingleInjectionManager
from flash_patcher.util.file_io import read_safe

class ReplaceContentManager:
    """Handle the replacement of a single content instance with specified text."""
    full_path: Path
    error_manager: ErrorManager

    def __init__(
        self: ReplaceContentManager,
        full_path: Path,
        error_manager: ErrorManager,
    ) -> None:
        self.full_path = full_path
        self.error_manager = error_manager

    def replace(
        self: ReplaceContentManager,
        ctx: PatchfileParser.LocationTokenContext,
        old_text: str,
        new_text: str,
    ) -> None:
        """Replace the specified instance of the old text with new text."""
        current_file = read_safe(self.full_path, self.error_manager)
        updated_file, replace_location = ParserFindContentManager(
            ctx, old_text.strip()
        ).resolve(current_file, self.error_manager)

        injector = SingleInjectionManager(
            self.full_path, replace_location, self.error_manager.patch_file, ctx.start.line
        )

        injector.file_content = updated_file
        injector.inject(new_text.strip(), ctx.start.line)

    def replace_all(
        self: ReplaceContentManager,
        old_text: str,
        new_text: str,
    ) -> None:
        """Replace all instances of the old text with the new text.
        This will go from the last to the first instance in order to avoid
        infinite loops or unintended behavior.
        """
        while True:
            current_file = read_safe(self.full_path, self.error_manager)

            try:
                updated_file, replace_location = LastFindContentManager(
                    old_text.strip()
                ).resolve(current_file, self.error_manager)
            except IndexError:
                # we've reached the last instance of the content
                break

            injector = SingleInjectionManager(
                self.full_path,
                replace_location,
                self.error_manager.patch_file,
                self.error_manager.line_no,
            )

            injector.file_content = updated_file
            injector.inject(new_text.strip(), self.error_manager.line_no)
