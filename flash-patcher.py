#!/usr/bin/python3
"""Riley's SWF patcher - a tool to patch content into SWF files.

Development: RileyTech, Kito
Bug testing: Creyon
Windows path fix: Jhynjhiruu

Download and updates: https://github.com/rayyaw/flash-patcher

License: CC-BY SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0)

Dependencies: Python 3, JPEXS Decompiler (https://github.com/jindrapetrik/jpexs-decompiler/releases)

Inject arbitrary code, images, and more into existing SWFs!
See the README for documentation and license.
"""

from __future__ import annotations

import argparse
import base64
import os
import shutil
import subprocess
import sys
from logging import basicConfig, critical, error, exception, info
from pathlib import Path

basicConfig(level=1, format="%(levelname)s: %(message)s")

CURRENT_VERSION = "v4.1.5"

DECOMP_LOCATION = Path("./.Patcher-Temp/mod/")
DECOMP_LOCATION_WITH_SCRIPTS = Path(DECOMP_LOCATION, "scripts/")

LOCATION_APT = Path("/usr/bin/ffdec")
LOCATION_FLATPAK = Path("/usr/bin/flatpak")
LOCATION_WINDOWS = Path(f"{os.getenv('PROGRAMFILES')}\\FFDec\\ffdec.exe")
LOCATION_WOW64 = Path(f"{os.getenv('PROGRAMFILES(X86)')}\\FFDec\\ffdec.exe")

ARGS_FLATPAK = [
    "run",
    "--branch=stable",
    "--arch=x86_64",
    "--command=ffdec.sh",
    "com.jpexs.decompiler.flash",
]


class JPEXSInterface:
    """An interface to interact with JPEXS via the shell."""

    path: Path
    args: list

    def __init__(self: JPEXSInterface, path: Path, args: list | None = None) -> None:
        self.path = path
        if args is None:
            self.args = []
        else:
            self.args = args

    def dump_xml(
        self: JPEXSInterface,
        inputfile: Path,
        output_dir: Path,
    ) -> subprocess.CompletedProcess:
        """Dump XML data of the input file into the output location."""
        return subprocess.run(
            [self.path, *self.args, "-swf2xml", inputfile, output_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

    def rebuild_xml(
        self: JPEXSInterface,
        input_dir: Path,
        output_file: Path,
    ) -> subprocess.CompletedProcess:
        """Rebuild XML data from a directory into an output SWF file."""
        return subprocess.run(
            [self.path, *self.args, "-xml2swf", input_dir, output_file],
            stdout=subprocess.DEVNULL,
            check=True,
        )

    def export_scripts(
        self: JPEXSInterface,
        inputfile: Path,
        output_dir: Path,
    ) -> subprocess.CompletedProcess:
        """Export scripts from a SWF file into a directory."""
        info("Exporting scripts into %s...", output_dir)
        return subprocess.run(
            [
                self.path,
                *self.args,
                "-export",
                "script",
                output_dir,
                inputfile,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )

    def recompile_data(
        self: JPEXSInterface,
        part: str,
        swf: Path,
        output: Path,
    ) -> int:
        """Recompile data of a given type into the SWF file."""
        info("Reimporting %ss...", part)
        return subprocess.run(
            [
                self.path,
                *self.args,
                f"-import{part}",
                swf,
                output,
                DECOMP_LOCATION,
            ],
            stdout=subprocess.DEVNULL,
            check=True,
        )


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
        """Add a line to be injected."""
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
                            "Invalid skip amount: ",
                            n,
                            "\n",
                            "Expected integer.\n",
                            "Aborting...",
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


def detect_jpexs() -> JPEXSInterface:
    """Detect and record JPEXS install location.

    Checks various common JPEXS paths
    Returns True if successful.
    """
    # apt install location
    if check_jpexs_exists(LOCATION_APT):
        return JPEXSInterface(LOCATION_APT)

    # flatpak install location
    if check_jpexs_exists(LOCATION_FLATPAK):
        # Detect if JPEXS is installed.
        # The function call can only detect if Flatpak is installed.
        testrun = subprocess.run(
            [LOCATION_FLATPAK, *ARGS_FLATPAK, "-help"],
            stdout=subprocess.DEVNULL,
            check=True,
        )

        if testrun.returncode == 0:
            return JPEXSInterface(LOCATION_FLATPAK, ARGS_FLATPAK)

    # windows default install location
    if check_jpexs_exists(LOCATION_WINDOWS):
        return JPEXSInterface(LOCATION_WINDOWS)

    # wow64 install location
    if check_jpexs_exists(LOCATION_WOW64):
        return JPEXSInterface(LOCATION_WOW64)

    return None


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
                for _i in range(line_start, line_end + 1):
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
            error(
                "Unrecognized command: '%s', skipping (at %s, line %d)",
                split_line[0],
                patch_file,
                current_line_no,
            )

        current_line_no += 1

    if line_add_mode:
        critical(
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
        line_stripped = line.strip(" \n\r")
        split_line = line_stripped.split(" ")

        if len(line_stripped) == 0 or line_stripped.startswith("#"):  # Comment
            continue

        if line_stripped.startswith("add-asset"):
            # Local copy of file, then remote
            local_name = split_line[1]
            remote_name = " ".join(split_line[2:])
            remote_name = line_stripped.split(" ")[2]

            if not Path(folder / local_name).exists():
                exception(
                    "Could not find asset: ",
                    local_name,
                    "\n",
                    "Aborting...",
                )
                sys.exit(1)

            # Create folder and copy things over
            remote_folder = remote_name.split("/")[0]

            if not (DECOMP_LOCATION / remote_folder).exists():
                Path.mkdir(DECOMP_LOCATION / remote_folder)

            shutil.copyfile(folder / local_name, DECOMP_LOCATION / remote_name)

            modified_files.add(DECOMP_LOCATION / remote_name)

        else:
            error("Unrecognized command: %s, skipping", line)

    return modified_files


def decompile_swf(
    iface: JPEXSInterface,
    inputfile: str,
    *,
    drop_cache: bool = False,
    xml_mode: bool = False,
) -> Path:
    """Decompile the SWF and return the decompilation location.

    This uses caching to save time.

    inputfile: the SWF to decompile
    drop_cache: if True, will force decompilation instead of using cached files
    """
    # Decompile swf into temp folder called ./.Patcher-Temp/[swf name, base32 encoded]
    if not Path("./.Patcher-Temp").exists():
        Path("./.Patcher-Temp").mkdir()

    if not inputfile.exists():
        error(
            """Could not locate the SWF file: %s.
            Aborting...""",
            inputfile,
        )
        sys.exit(1)

    cache_location = Path(
        "./.Patcher-Temp/",
        base64.b32encode(
            bytes(inputfile.name, "utf-8"),
        ).decode("ascii"),
    )

    if xml_mode:
        info("XML decompilation mode.")
        global DECOMP_LOCATION
        global DECOMP_LOCATION_WITH_SCRIPTS

        cache_location = Path("./.Patcher-Temp/swf2.xml")

        DECOMP_LOCATION = Path("./.Patcher-Temp/swf.xml")
        DECOMP_LOCATION_WITH_SCRIPTS = Path("./.Patcher-Temp/")

    # Mkdir / check for cache
    if drop_cache or (not Path(cache_location).exists()):
        if not Path(cache_location).exists() and not xml_mode:
            Path(cache_location).mkdir()

        info("Beginning decompilation...")

        decomp = None

        if xml_mode:
            decomp = iface.dump_xml(inputfile, cache_location)
            info("XML decompilation mode.")
        else:
            decomp = iface.export_scripts(inputfile, cache_location)

        if decomp.returncode != 0:
            error(
                """JPEXS couldn't decompile the SWF file: %s.
                Aborting...""",
                inputfile,
            )
            sys.exit(1)

    else:
        info("Detected cached decompilation. Skipping...")

    return cache_location


def recompile_swf(
    iface: JPEXSInterface,
    inputfile: Path,
    output: Path,
    *,
    recompile_all: bool,
    xml_mode: bool,
) -> None:
    """Recompile the SWF after injection is complete.

    inputfile: The base SWF to use for missing files
    outputfile: The location to save the output
    recompile_all: If this is set to False, will only recompile scripts
    """
    # Repackage the file as a SWF
    # Rant: JPEXS should really return an error code if recompilation fails here!
    # Unable to detect if this was successful or not otherwise.
    if xml_mode:
        iface.rebuild_xml(DECOMP_LOCATION, output)
        return

    iface.recompile_data("Script", inputfile, output)

    if recompile_all:
        for part in ("Images", "Sounds", "Shapes", "Text"):
            # JPEXS doesn't have a way to import everything at once.
            # We re-import iteratively.
            iface.recompile_data(part, output, output)


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
        patch_stripped = patch.strip("\r\n ")
        if len(patch_stripped) == 0 or patch_stripped[0] == "#":
            continue

        # Check file extension of file
        if patch_stripped.endswith(".patch"):  # Patch (code) file
            modified_scripts |= apply_patch(folder / patch_stripped)
        elif patch_stripped.endswith(".assets"):  # Asset Pack file
            modified_scripts |= apply_assets(folder / patch_stripped, folder)
        else:
            exception(
                "The file provided ('",
                patch_stripped,
                "') did not have a valid filetype.\n",
                "Aborting...",
            )
            sys.exit(1)

    return modified_scripts


def main(
    inputfile: Path,
    folder: Path,
    stagefile: Path,
    output: Path,
    *,
    drop_cache: bool,
    recompile_all: bool,
    xml_mode: bool,
) -> None:
    """Run the patcher."""
    info("Riley's SWF Patcher - %s", CURRENT_VERSION)

    jpexs_iface = detect_jpexs()
    if jpexs_iface is None:
        error(
            "Could not locate required dependency: JPEXS Flash Decompiler. Aborting...",
        )
        sys.exit(1)

    info("Using JPEXS at: %s", jpexs_iface.path)

    cache_location = decompile_swf(
        jpexs_iface,
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

    recompile_swf(
        jpexs_iface,
        inputfile,
        output,
        recompile_all=recompile_all,
        xml_mode=xml_mode,
    )

    info("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--inputswf",
        dest="input_swf",
        type=str,
        required=True,
        help="Input SWF file",
    )
    parser.add_argument(
        "--folder",
        dest="folder",
        type=str,
        required=True,
        help="Folder with patch files",
    )
    parser.add_argument(
        "--stagefile",
        dest="stage_file",
        type=str,
        required=True,
        help="Stage file name",
    )
    parser.add_argument(
        "--outputswf",
        dest="output_swf",
        type=str,
        required=True,
        help="Output SWF file",
    )

    parser.add_argument(
        "--invalidateCache",
        dest="drop_cache",
        default=False,
        action="store_true",
        help="Invalidate cached decompilation files",
    )
    parser.add_argument(
        "--all",
        dest="recompile_all",
        default=False,
        action="store_true",
        help="Recompile the whole SWF (if this is off, only scripts will recompile)",
    )
    parser.add_argument(
        "--xml",
        dest="xml_mode",
        default=False,
        action="store_true",
        help="Inject into an XML decompilation instead of standard syntax",
    )

    args = parser.parse_args()

    main(
        Path(args.input_swf),
        Path(args.folder),
        Path(args.stage_file),
        Path(args.output_swf),
        drop_cache=args.drop_cache,
        recompile_all=args.recompile_all,
        xml_mode=args.xml_mode,
    )
