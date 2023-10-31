from __future__ import annotations

import os
import shutil
import sys
from logging import basicConfig, error, exception, info, warning
from pathlib import Path

from compile.compilation import CompilationManager

"""Riley's SWF patcher - a tool to patch content into SWF files.

Development: RileyTech, qtkito, GTcreyon
Windows path fix: Jhynjhiruu

Download and updates: https://github.com/rayyaw/flash-patcher

License: CC-BY SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0)

Dependencies: Python 3, JPEXS Decompiler (https://github.com/jindrapetrik/jpexs-decompiler/releases)

Inject arbitrary code, images, and more into existing SWFs!
See the README for documentation and license.
"""

basicConfig(level=1, format="%(levelname)s: %(message)s")

CURRENT_VERSION = "v4.1.7"

DECOMP_LOCATION = Path("./.Patcher-Temp/mod/")
DECOMP_LOCATION_WITH_SCRIPTS = Path(DECOMP_LOCATION, "scripts/")

class FilePosition:
    """A position in a named file."""

    def __init__(self: FilePosition, file_name: str) -> None:
        self.fileName = file_name
        self.lineNumber = 0

class CodeInjector:
    """Handles injection of code into script files."""

    def __init__(self: CodeInjector) -> None:
        self.files = []
        self.fileContents = {}
        self.injectLines = []
        self.startingLineNo = -1

    # Return the file name of the script being modified
    def add_injection_target(
        self: CodeInjector,
        injection_info: list,
        patch_file: Path,
        current_line_no: int,
    ) -> str:
        """Add an injection target to this injector."""
        split_line = injection_info.split()
        short_name = " ".join(split_line[1:-1])
        file_name = DECOMP_LOCATION_WITH_SCRIPTS / short_name

        file_content = read_from_file(file_name, patch_file, current_line_no)
        current_file = FilePosition(file_name)

        split_line = injection_info.split()

        current_file.lineNumber = find_write_location(file_content, split_line[-1])
        self.files.append(current_file)
        self.fileContents[file_name] = file_content
        return file_name

    def add_injection_line(
        self: CodeInjector,
        line: str,
        current_line_no: int,
    ) -> None:
        """Queue a line to be injected.

        The line will not be injected immediately.
        It will be injected once inject() is called.
        """
        self.injectLines.append(line)

        if self.startingLineNo == -1:
            self.startingLineNo = current_line_no

    def inject(self: CodeInjector) -> None:
        """Perform loaded injections."""
        if len(self.injectLines) == 0:
            return

        # Inject into every file
        for file in self.files:
            patch_line_no = self.startingLineNo
            file_line_no = file.lineNumber

            for line in self.injectLines:
                line_stripped = line.strip("\n\r ")
                split_line = line_stripped.split()

                # Handle internal commands
                if split_line[:2] == ["//", "cmd:", "skip"]:
                    n_str = split_line[3]
                    try:
                        n = int(n_str)
                        continue
                    except ValueError:
                        exception(
                            """Invalid skip amount: %s.
                            Expected integer.
                            Aborting...""",
                            n_str,
                        )
                        sys.exit(1)

                    file_line_no += n

                self.fileContents[file.fileName].insert(file_line_no, line)

                patch_line_no += 1
                file_line_no += 1

        for file, file_content in self.fileContents.items():
            write_to_file(file, file_content)


def check_jpexs_exists(path: str) -> bool:
    """Check if JPEXS exists at a given path.

    Returns True if successful, and False otherwise.
    """
    return path.exists()

def read_from_file(file_location: Path, patch_file: Path, current_line_no: int) -> list:
    """Read all lines from a file.

    Returns a list, with one entry for each line.
    """
    try:
        with Path.open(file_location) as f:
            return f.readlines()
    except (FileNotFoundError, IsADirectoryError):
        exception(
            """%s, line %d: Invalid injection location.
            Could not find or load SWF decompiled file at: %s
            Aborting...""",
            patch_file,
            current_line_no,
            file_location,
        )
        sys.exit(1)

def write_to_file(path: Path, lines: list) -> None:
    """Write a list of lines to a file."""
    with Path.open(path, "w") as f:
        f.writelines(lines)

def find_write_location(lines: list, code: str) -> None:
    """Find the location in the file specified.

    If code is an integer, it'll resolve to writing AFTER that line number.
    If code is "end", it'll resolve to the end of that file.
    """
    if code == "end":
        return len(lines)

    try:
        return int(code) - 1
    except ValueError:
        exception(
            """Invalid add location: %s
            Expected keyword or integer (got type "str").
            Aborting...""",
            code,
        )
        sys.exit(1)

def apply_patch(patch_file: Path) -> set:
    """Apply a single patch file.

    patch_file parameter: The path to the patch file.
    """
    modified_scripts = set()
    lines = []

    # Read all lines from file
    try:
        with Path.open(patch_file) as f:
            lines = f.readlines()
    except FileNotFoundError:
        exception(
            """Could not open Patchfile: %s
            Aborting...""",
            patch_file,
        )
        sys.exit(1)

    line_add_mode = False
    file_location = ""

    current_line_no = 1

    injector = None

    for line in lines:
        line_stripped = line.strip("\n\r ")

        # Ignore comments and blank lines
        if len(line_stripped) == 0 or line[0] == "#":
            current_line_no += 1
            continue

        split_line = line_stripped.split()

        # HANDLE ADD STATEMENT ----
        # If we have an add command, set the adding location and switch to add mode
        if split_line[0] == "add":
            if injector is None:
                injector = CodeInjector()

            script = injector.add_injection_target(
                line_stripped,
                patch_file,
                current_line_no,
            )
            modified_scripts.add(script)

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
                    patch_file,
                    current_line_no,
                )
                sys.exit(1)

            injector.inject()
            injector = None

        elif line_add_mode:
            injector.add_injection_line(line, current_line_no)

        # HANDLE REMOVE STATEMENT ----
        elif split_line[0] == "remove":
            # Account for spaces in file name.
            # Take everything except the first and last blocks.
            # The first block is the command character.
            # The last block is the line number(s).
            short_name = " ".join(split_line[1:-1])
            file_location = DECOMP_LOCATION_WITH_SCRIPTS / short_name

            # Add the current script to the list of modified ones,
            # i.e. keep this in the final output.
            modified_scripts.add(file_location)

            current_file = read_from_file(file_location, patch_file, current_line_no)
            line_counts = split_line[-1].split("-")

            if len(line_counts) != 2:
                exception(
                    """%s, line %d: Invalid syntax.
                    Expected two integers, separated by a dash (-) (at %s)""",
                    patch_file,
                    current_line_no,
                    line_stripped,
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
                    patch_file,
                    current_line_no,
                    split_line[-1],
                )
                sys.exit(1)

            try:
                for _ in range(line_start, line_end + 1):
                    del current_file[line_start - 1]
            except IndexError:
                exception(
                    """%s, line %d: Out of range.
                    Line number %d out of range for file %s.
                    Aborting...""",
                    patch_file,
                    current_line_no,
                    line_end,
                    file_location,
                )
                sys.exit(1)

            write_to_file(file_location, current_file)

        # Unrecognized statement
        else:
            warning(
                "Unrecognized command: '%s', skipping (at %s, line %d)",
                split_line[0],
                patch_file,
                current_line_no,
            )

        current_line_no += 1

    if line_add_mode:
        error(
            """%s: Syntax error.
            Missing end-patch for "add" on line %d.
            Aborting...""",
            patch_file,
            injector.startingLineNo - 1,
        )
        sys.exit(1)

    # Return the set of modified scripts, so we can aggregate in main()
    return modified_scripts


def apply_assets(asset_file: Path, folder: Path) -> set:
    """Apply asset packs to files in a folder."""
    modified_files = set()
    lines = []

    try:
        with Path.open(asset_file) as f:
            lines = f.readlines()
    except FileNotFoundError:
        exception(
            """Could not open asset pack file at: %s.
            Aborting...""",
            asset_file,
        )
        sys.exit(1)

    for line in lines:
        line_stripped = line.strip("\n\r ")
        split_line = line_stripped.split(" ")

        if len(line_stripped) == 0 or line_stripped.startswith("#"):  
            # Lines that start with # are comments
            continue

        if line_stripped.startswith("add-asset"):
            # Local copy of file, then remote
            local_name = split_line[1]
            remote_name = " ".join(split_line[2:])
            remote_name = line_stripped.split(" ")[2]

            if not Path(folder / local_name).exists():
                exception(
                    """Could not find asset: %s
                    Aborting...""",
                    local_name,
                )
                sys.exit(1)

            # Create folder and copy things over
            remote_folder = remote_name.split("/")[0]

            if not (DECOMP_LOCATION / remote_folder).exists():
                Path.mkdir(DECOMP_LOCATION / remote_folder)

            shutil.copyfile(folder / local_name, DECOMP_LOCATION / remote_name)

            modified_files.add(DECOMP_LOCATION / remote_name)

        else:
            warning("Unrecognized command: %s, skipping", line)

    return modified_files

def clean_scripts(modified_scripts: set) -> None:
    """Delete all non-modified scripts.

    Taken from https://stackoverflow.com/questions/19309667/recursive-os-listdir
    - Make recursive os.listdir.
    """
    scripts = [
        Path(dp, f) for dp, dn, fn in os.walk(DECOMP_LOCATION.expanduser()) for f in fn
    ]
    for script in scripts:
        if script not in modified_scripts:
            script.unlink()


def apply_patches(patches: list, folder: Path) -> set:
    """Apply every patch, ignoring comments and empty lines."""
    modified_scripts = set()
    for patch in patches:
        patch_stripped = patch.strip("\n\r ")
        if len(patch_stripped) == 0 or patch_stripped[0] == "#":
            continue

        # Check file extension of file
        if patch_stripped.endswith(".patch"):  # Patch (code) file
            modified_scripts |= apply_patch(folder / patch_stripped)
        elif patch_stripped.endswith(".assets"):  # Asset Pack file
            modified_scripts |= apply_assets(folder / patch_stripped, folder)
        else:
            exception(
                """The file provided ('%s') did not have a valid filetype.
                Aborting...""",
                patch_stripped,
            )
            sys.exit(1)

    return modified_scripts

def main(
    inputfile: Path,
    folder: Path,
    stagefile: Path,
    output: Path,
    drop_cache: bool,
    recompile_all: bool,
    xml_mode: bool,
) -> None:
    """Run the patcher."""
    info("Riley's SWF Patcher - %s", CURRENT_VERSION)

    try:
        compiler = CompilationManager()
    except ModuleNotFoundError:
        exception(
            "Could not locate required dependency: JPEXS Flash Decompiler. Aborting...",
        )
        sys.exit(1)

    if xml_mode:
        info("XML decompilation mode.")
        global DECOMP_LOCATION
        global DECOMP_LOCATION_WITH_SCRIPTS

        DECOMP_LOCATION = Path("./.Patcher-Temp/swf.xml")
        DECOMP_LOCATION_WITH_SCRIPTS = Path("./.Patcher-Temp/")

    cache_location = compiler.decompile(
        inputfile,
        drop_cache=drop_cache,
        xml_mode=xml_mode,
    )

    # Copy the cache to a different location so we can reuse it
    isdir = cache_location.is_dir()
    if DECOMP_LOCATION.exists():
        if isdir:
            shutil.rmtree(DECOMP_LOCATION)
        else:
            Path.unlink(DECOMP_LOCATION)

    if isdir:
        shutil.copytree(cache_location, DECOMP_LOCATION)
    else:
        shutil.copy(cache_location, DECOMP_LOCATION)

    info("Decompilation finished. Beginning injection...")

    try:
        # Open the stage file and read list of all patches to apply
        with Path.open(folder / stagefile) as f:
            patches_to_apply = f.readlines()
    except FileNotFoundError:
        exception(
            """Could not open stage file: %s.
            Aborting...""",
            Path(folder / stagefile),
        )
        sys.exit(1)

    modified_scripts = apply_patches(patches_to_apply, folder)

    info("Injection complete, cleaning up...")

    clean_scripts(modified_scripts)

    info("Recompiling...")

    compiler.recompile(
        DECOMP_LOCATION,
        inputfile,
        output,
        recompile_all=recompile_all,
        xml_mode=xml_mode,
    )

    info("Done.")
