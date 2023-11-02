from __future__ import annotations

import sys
from logging import error, exception, warning
from pathlib import Path

from inject.bulk_injection import BulkInjectionManager
from inject.injection_location import InjectionLocation
from inject.single_injection import SingleInjectionManager
from util.exception import InjectionErrorManager
from util.file_io import read_from_file, write_to_file

class PatchFileParser:
    patchFile: Path
    decompLocationWithScripts: Path

    modifiedScripts: set
    lineNo: int

    def __init__(
        self: PatchFileParser,
        patch_file: Path,
        decomp_location_with_scripts: Path
    ) -> None:
        self.patchFile = patch_file
        self.decompLocationWithScripts = decomp_location_with_scripts

        self.modifiedScripts = set()
        self.lineNo = 0

        # Read all lines from file
        try:
            with Path.open(patch_file) as f:
                self.fileContent = f.readlines()
        except FileNotFoundError:
            exception(
                """Could not open Patchfile: %s
                Aborting...""",
                patch_file,
            )
            sys.exit(1)

    def parse(self: PatchFileParser) -> set:
        """Apply a single patch file."""
        line_add_mode = False
        self.lineNo = 1
        injector = None

        for line in self.fileContent:
            line_stripped = line.strip("\n\r ")

            # Ignore comments and blank lines
            if len(line_stripped) == 0 or line[0] == "#":
                self.lineNo += 1
                continue

            split_line = line_stripped.split()

            # HANDLE ADD STATEMENT ----
            # If we have an add command, set the adding location and switch to add mode
            if split_line[0] == "add":
                if injector is None:
                    injector = BulkInjectionManager()

                inject_location = InjectionLocation(split_line[-1])
                add_file_location = self.decompLocationWithScripts / ' '.join(split_line[1:-1])
                single_injector = SingleInjectionManager(
                    add_file_location,
                    inject_location,
                    self.patchFile,
                    self.lineNo
                )
                
                injector.add_injection_target(single_injector)
                self.modifiedScripts.add(add_file_location)

            elif split_line[0] == "begin-patch":
                line_add_mode = True

            # If we're in add mode and encounter the end of the patch,
            # write the modified script back to file.
            elif line_stripped == "end-patch" and line_add_mode:
                line_add_mode = False

                if injector is None:
                    exception(
                        """%s, line %d: Invalid syntax.
                        end-patch is not matched by any 'add' statements.""",
                        self.patchFile,
                        self.lineNo,
                    )
                    sys.exit(1)

                injector.inject()
                injector = None

            elif line_add_mode:
                injector.add_injection_line(line, self.lineNo)

            # HANDLE REMOVE STATEMENT ----
            elif split_line[0] == "remove":
                self.parseRemove(split_line)
            # Unrecognized statement
            else:
                warning(
                    "Unrecognized command: '%s', skipping (at %s, line %d)",
                    split_line[0],
                    self.patchFile,
                    self.lineNo,
                )

            self.lineNo += 1

        if line_add_mode:
            error(
                """%s: Syntax error.
                Missing end-patch for "add" on line %d.
                Aborting...""",
                self.patchFile,
                injector.startingLineNo - 1,
            )
            sys.exit(1)

        # Return the set of modified scripts
        return self.modifiedScripts

    def parseRemove(self: PatchFileParser, split_line: list) -> None:
        # Account for spaces in file name.
        # Take everything except the first and last blocks.
        # The first block is the command character.
        # The last block is the line number(s).
        short_name = " ".join(split_line[1:-1])
        file_location = self.decompLocationWithScripts / short_name

        # Add the current script to the list of modified ones,
        # i.e. keep this in the final output.
        self.modifiedScripts.add(file_location)

        error_manager = InjectionErrorManager(self.patchFile, self.lineNo)
        current_file = read_from_file(file_location, error_manager)
        line_counts = split_line[-1].split("-")

        # Parse remove start and end sections
        if len(line_counts) != 2:
            exception(
                """%s, line %d: Invalid syntax.
                Expected two integers, separated by a dash (-) (at %s)""",
                self.patchFile,
                self.lineNo,
                " ".join(split_line),
            )
            sys.exit(1)

        try:
            line_start = int(line_counts[0])
            line_end = int(line_counts[1])
        except ValueError:
            exception(
                """%s, line %d: Invalid syntax.
                Invalid line numbers provided: %s
                Aborting...""",
                self.patchFile,
                self.lineNo,
                split_line[-1],
            )
            sys.exit(1)

        # Open file, delete lines, and close it
        try:
            for _ in range(line_start, line_end + 1):
                del current_file[line_start - 1]
        except IndexError:
            exception(
                """%s, line %d: Out of range.
                Line number %d out of range for file %s.
                Aborting...""",
                self.patchFile,
                self.lineNo,
                line_end,
                file_location,
            )
            sys.exit(1)

        write_to_file(file_location, current_file)

