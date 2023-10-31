from __future__ import annotations

import sys
from pathlib import Path

from .injection_location import InjectionLocation
from ..util.exception import InjectionErrorManager
from ..util.file_io import read_from_file, write_to_file

class SingleInjectionManager:
    """A position in a named file."""

    def __init__(
            self: SingleInjectionManager, 
            file_name: Path,
            file_location: InjectionLocation,
            patch_file: Path,
        ) -> None:
        self.fileName = file_name         # file to inject into
        self.fileLocation = file_location # location to inject at

        self.patchFile = patch_file       # name of the patch file

        self.fileContent = read_from_file(self.fileName, self.patchFile, self.patchLineNo)
        self.errorManager = InjectionErrorManager(self.patchFile.as_posix(), 0, None)
    
    def inject(self: SingleInjectionManager, content: list, patch_file_line: int) -> None:
        """
        Inject the content into the file.
        """
        # Inject into every file
        patch_line_no = patch_file_line
        file_line_no = self.fileLocation.resolve(self.fileContent, self.patchLineNo)

        for line in content:
            line_stripped = line.strip("\n\r ")

            # setup error information for the current line
            self.errorManager.lineNo = patch_line_no
            self.errorManager.extraInfo = line_stripped

            # Handle internal commands
            patch_line_no, was_secondary = self.handle_secondary_command(patch_line_no, line_stripped)

            # No internal command, just a normal line
            if not was_secondary:
                self.file_content.insert(file_line_no, line)
                file_line_no += 1
            
            patch_line_no += 1

        write_to_file(self.fileName, self.file_content)

    def handle_secondary_command(
        self: SingleInjectionManager, 
        old_line_no: int,
        command: str,
    ) -> (int, bool):
        """
        Handle a secondary command within the patch file itself, for example:
        // cmd: skip 10
        This takes in the current line no. we're injecting at and the command.
        Returns the new line no. after the command, and a boolean on whether any command was executed.
        """
        command_split = command.split()
        if command_split[:1] == ["//", "cmd:"]:
            # command found
            new_line_no, was_skip = self.handle_secondary_skip_command(old_line_no, command)
            if (was_skip):
                return new_line_no, was_skip
            
            self.errorManager.throw(
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
        """
        Handle a secondary skip command of the form:
        // cmd: skip 10
        This will skip 10 lines ahead within the file.
        Returns True if the command is a valid skip command, and updates the line no. accordingly.
        """
        split_line = command.split()
        if split_line[2] == "skip":
            n_str = split_line[3]
            try:
                n = int(n_str)
                file_line_no = old_line_no + n
                return file_line_no, True
            except ValueError:
                self.errorManager.throw(
                    """Invalid skip amount.
                    Expected integer.""",
                )
                sys.exit(1)

        return old_line_no, False 