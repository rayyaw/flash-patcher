from __future__ import annotations

import os
import subprocess
from logging import info
from pathlib import Path

LOCATION_APT = Path("/usr/bin/ffdec")
LOCATION_FLATPAK = Path("/usr/bin/flatpak")
LOCATION_WINDOWS = Path(f"{os.getenv('PROGRAMFILES')}\\FFDec\\ffdec.bat")
LOCATION_WOW64 = Path(f"{os.getenv('PROGRAMFILES(X86)')}\\FFDec\\ffdec.bat")

ARGS_FLATPAK = [
    "run",
    "--branch=stable",
    "--arch=x86_64",
    "--command=ffdec.sh",
    "com.jpexs.decompiler.flash",
]

class JPEXSInterface:
    """An interface to interact with JPEXS via the shell.

    This class should only be used for functions that have a one-to-one correspondence
    with JPEXS CLI commands.
    For anything more sophisticated, you should use the CompilationManager class instead.
    """

    path: Path
    args: list

    def __init__(self: JPEXSInterface, path: Path | None = None, args: list | None = None) -> None:
        """Initialize by detecting JPEXS, or using a provided version"""
        if path is not None:
            self.path = path
            if args is None:
                self.args = []
            else:
                self.args = args

            info("Using JPEXS at: %s", path)

        else:
            # Auto-detect JPEXS at any of the default locations
            jpexs_installed = any([
                self.install_jpexs(LOCATION_APT),
                self.install_jpexs(LOCATION_FLATPAK, ARGS_FLATPAK),
                self.install_jpexs(LOCATION_WINDOWS),
                self.install_jpexs(LOCATION_WOW64),
            ])

            if not jpexs_installed:
                raise ModuleNotFoundError("Failed to locate dependency: JPEXS Flash Decompiler")

            info("Using JPEXS at: %s", self.path)

    def install_jpexs(self, path: Path, args: list | None = None) -> bool:
        """Install JPEXS from a path. Return true if the installation was successful."""
        if path.exists() and args is None:
            # Normal JPEXS install, we're just running ffdec.sh directly
            self.path = path
            self.args = []
            return True

        if path.exists():
            # We're running JPEXS through a sandbox or proxy (like Flatpak)
            # path.exists() checks that the path exists, but not that JPEXS is installed
            # so we need to run jpexs -help to verify it's installed correctly
            testrun = subprocess.run(
                [path, *args, "-help"],
                stdout=subprocess.DEVNULL,
                check=True,
            )

            if testrun.returncode == 0:
                self.path = path
                self.args = args
                return True

        return False

    def dump_xml(
        self: JPEXSInterface,
        inputfile: Path,
        output_dir: Path,
    ) -> bool:
        """Dump XML data of the input file into the output location.

        Returns True if dump was successful.
        """
        process =  subprocess.run(
            [self.path, *self.args, "-swf2xml", inputfile, output_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return process.returncode == 0

    def rebuild_xml(
        self: JPEXSInterface,
        input_dir: Path,
        output_file: Path,
    ) -> bool:
        """Rebuild XML data from a directory into an output SWF file.

        Return True on success.
        """
        process = subprocess.run(
            [self.path, *self.args, "-xml2swf", input_dir, output_file],
            stdout=subprocess.DEVNULL,
            check=True,
        )
        return process.returncode == 0

    def export_scripts(
        self: JPEXSInterface,
        inputfile: Path,
        output_dir: Path,
    ) -> bool:
        """Export scripts from a SWF file into a directory.
        
        Returns True on success.
        """
        info("Exporting scripts into %s...", output_dir)
        process = subprocess.run(
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

        return process.returncode == 0

    def recompile_data(
        self: JPEXSInterface,
        part: str,
        decomp_location: Path,
        swf: Path,
        output: Path,
    ) -> int:
        """Recompile data of a given type into the SWF file."""
        # Part types: SymbolClass, Movies, Sounds, Shapes, Images, Text, Script
        info("Reimporting %s...", part)
        return subprocess.run(
            [
                self.path,
                *self.args,
                f"-import{part}",
                swf,
                output,
                decomp_location,
            ],
            stdout=subprocess.DEVNULL,
            check=True,
        )
