from __future__ import annotations

from pathlib import Path

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.inject.location.injection_location import InjectionLocation
from flash_patcher.util.file_io import readlines_safe, writelines_safe

class SingleInjectionManager:
    """A position in a named file."""

    # file to inject into
    file_name: Path

    # location to inject at
    file_location: InjectionLocation

    # name of the patch file
    patch_file: Path

    # line number within the pacth file
    patch_line_no: int

    error_manager: ErrorManager
    file_content: list[str]

    def __init__(
        self: SingleInjectionManager,
        file_name: Path,
        file_location: InjectionLocation,
        patch_file: Path,
        patch_line_no: int,
    ) -> None:
        self.file_name = file_name
        self.file_location = file_location
        self.file_content = None

        self.patch_file = patch_file
        self.patch_line_no = patch_line_no

        self.error_manager = ErrorManager(self.patch_file.as_posix(), 0, None)

    def inject(self: SingleInjectionManager, content: list[str], patch_file_line: int) -> None:
        """Inject the content into the file."""
        patch_line_no = patch_file_line

        if self.file_content is None:
            self.file_content = readlines_safe(self.file_name, self.error_manager)

        file_line_no = self.file_location.resolve(self.file_content, True, self.error_manager)

        if file_line_no is None:
            return

        for line in content:
            line_stripped = line.strip("\n\r ")

            # setup error information for the current line
            self.error_manager.patch_file = self.patch_file
            self.error_manager.line_no = patch_line_no
            self.error_manager.context = line_stripped

            # Handle internal commands
            file_line_no, was_secondary = self.handle_secondary_command(
                file_line_no, line_stripped
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
        match command_split[:3]:
            case ["//", "cmd:", "skip"]:
                # command found
                new_line_no = self.handle_secondary_skip_command(old_line_no, command)
                return new_line_no, True

            case ["//", "cmd:", _]:
                self.error_manager.raise_(
                    """Invalid secondary command.
                    Expected one of: [skip].""",
                )

        return old_line_no, False

    def handle_secondary_skip_command(
        self: SingleInjectionManager,
        old_line_no: int,
        command: str,
    ) -> int:
        """Handle a secondary skip command of the form: // cmd: skip 10

        This will skip 10 lines ahead within the file.
        Returns True if the command is a valid skip command, and updates the line no. accordingly.
        """

        split_line = command.split()
        n_str = split_line[3]

        try:
            skip_amount = int(n_str)
            file_line_no = old_line_no + skip_amount
            return file_line_no

        except ValueError:
            self.error_manager.raise_(
                """Invalid skip amount.
                Expected integer.""",
            )
