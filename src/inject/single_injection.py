from __future__ import annotations

import sys
from pathlib import Path

from exception_handle.error_manager import ErrorManager
from inject.injection_location import InjectionLocation
from util.file_io import readlines_safe, writelines_safe

class SingleInjectionManager:
    """A position in a named file."""

    file_name: Path
    file_location: InjectionLocation

    patch_file: Path
    patch_line_no: int

    error_manager: ErrorManager
    file_content: list

    def __init__(
        self: SingleInjectionManager,
        file_name: Path,
        file_location: InjectionLocation,
        patch_file: Path,
        patch_line_no: int,
    ) -> None:
        self.file_name = file_name         # file to inject into
        self.file_location = file_location # location to inject at

        self.patch_file = patch_file       # name of the patch file
        self.patch_line_no = patch_line_no  # line number within the patch file

        self.error_manager = ErrorManager(self.patch_file.as_posix(), 0, None)
        self.file_content = readlines_safe(self.file_name, self.error_manager)

    def inject(self: SingleInjectionManager, content: list, patch_file_line: int) -> None:
        """Inject the content into every file."""
        patch_line_no = patch_file_line
        file_line_no = self.file_location.resolve(self.file_content, self.patch_line_no)

        for line in content:
            line_stripped = line.strip("\n\r ")

            # setup error information for the current line
            self.error_manager.patch_file = self.patch_file
            self.error_manager.line_no = patch_line_no
            self.error_manager.context = line_stripped

            # Handle internal commands
            patch_line_no, was_secondary = self.handle_secondary_command(
                patch_line_no, line_stripped
            )

            # No internal command, just a normal line
            if not was_secondary:
                self.file_content.insert(file_line_no, line)
                file_line_no += 1

            patch_line_no += 1

        writelines_safe(self.file_name, self.file_content)

    def handle_secondary_command(
        self: SingleInjectionManager,
        old_line_no: int,
        command: str,
    ) -> (int, bool):
        """Handle a secondary command within the patch file itself.
        
        For example:
        // cmd: skip 10
        This takes in the current line no. we're injecting at and the command.
        Returns the new line no. after the command, 
        and a boolean on whether any command was executed.
        """
        command_split = command.split()
        if command_split[:1] == ["//", "cmd:"]:
            # command found
            new_line_no, was_skip = self.handle_secondary_skip_command(old_line_no, command)
            if was_skip:
                return new_line_no, was_skip

            self.error_manager.throw(
                """Invalid secondary command.
                Expected one of: [skip].""",
            )

        else:
            return old_line_no, False

    def handle_secondary_skip_command(
        self: SingleInjectionManager,
        old_line_no: int,
        command: str,
    ) -> (int, bool):
        """Handle a secondary skip command of the form: // cmd: skip 10

        This will skip 10 lines ahead within the file.
        Returns True if the command is a valid skip command, and updates the line no. accordingly.
        """
        split_line = command.split()
        if split_line[2] == "skip":
            n_str = split_line[3]
            try:
                skip_amount = int(n_str)
                file_line_no = old_line_no + skip_amount
                return file_line_no, True
            except ValueError:
                self.error_manager.throw(
                    """Invalid skip amount.
                    Expected integer.""",
                )
                sys.exit(1)

        return old_line_no, False
