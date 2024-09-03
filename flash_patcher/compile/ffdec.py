from __future__ import annotations

import os
import subprocess
from pathlib import Path

from flash_patcher.util.logging import logger

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

class FFDecInterface:
    """An interface to interact with FFDec via the shell.

    This class should only be used for functions that have a one-to-one correspondence
    with FFDec CLI commands.
    For anything more sophisticated, you should use the CompilationManager class instead.
    """

    path: Path
    args: list[str]

    def __init__(
        self: FFDecInterface,
        path: Path | None = None,
        args: list[str] | None = None,
    ) -> None:
        """Initialize by detecting FFDec, or using a provided version"""
        if path is not None:
            self.path = path
            if args is None:
                self.args = []
            else:
                self.args = args

            logger.info("Using FFDec at: %s", path)

        else:
            # Auto-detect FFDec at any of the default locations
            ffdec_installed = any([
                self.install_ffdec(LOCATION_APT),
                self.install_ffdec(LOCATION_FLATPAK, ARGS_FLATPAK),
                self.install_ffdec(LOCATION_WINDOWS),
                self.install_ffdec(LOCATION_WOW64),
            ])

            if not ffdec_installed:
                raise ModuleNotFoundError(
                    """Failed to locate dependency: JPEXS Flash Decompiler.
                    You can download FFDec from this link:
                    https://github.com/jindrapetrik/jpexs-decompiler/releases
                    """
                )

            logger.info("Using FFDec at: %s", self.path)

    def install_ffdec(self: FFDecInterface, path: Path, args: list[str] | None = None) -> bool:
        """Install FFDec from a path. Return true if the installation was successful."""
        if path.exists() and args is None:
            # Normal FFDec install, we're just running ffdec.sh directly
            self.path = path
            self.args = []
            return True

        if path.exists():
            # We're running FFDec through a sandbox or proxy (like Flatpak)
            # path.exists() checks that the path exists, but not that FFDec is installed
            # so we need to run ffdec -help to verify it's installed correctly
            testrun = subprocess.run(
                [path, *args, "-help"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

            if testrun.returncode == 0:
                self.path = path
                self.args = args
                return True

        return False

    def dump_xml(
        self: FFDecInterface,
        inputfile: Path,
        output_dir: Path,
    ) -> bool:
        """Dump XML data of the input file into the output location.

        Returns True if dump was successful.
        """
        process = subprocess.run(
            [self.path, *self.args, "-swf2xml", inputfile, output_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return process.returncode == 0

    def rebuild_xml(
        self: FFDecInterface,
        input_dir: Path,
        output_file: Path,
    ) -> bool:
        """Rebuild XML data from a directory into an output SWF file.

        Return True on success.
        """
        process = subprocess.run(
            [self.path, *self.args, "-xml2swf", input_dir, output_file],
            stdout=subprocess.DEVNULL,
            check=False,
        )
        return process.returncode == 0

    def export_scripts(
        self: FFDecInterface,
        inputfile: Path,
        output_dir: Path,
    ) -> bool:
        """Export scripts from a SWF file into a directory.
        
        Returns True on success.
        """
        logger.info("Exporting scripts into %s...", output_dir)

        # set check=False, we will verify the return code manually later
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
            check=False,
        )

        return process.returncode == 0

    def recompile_data(
        self: FFDecInterface,
        part: str,
        decomp_location: Path,
        swf: Path,
        output: Path,
    ) -> bool:
        """Recompile data of a given type into the SWF file."""

        # Part types: SymbolClass, Movies, Sounds, Shapes, Images, Text, Script
        logger.info("Reimporting %s...", part)

        # set check=False, we will verify the return code manually later
        process = subprocess.run(
            [
                self.path,
                *self.args,
                f"-import{part}",
                swf,
                output,
                decomp_location,
            ],
            stdout=subprocess.DEVNULL,
            check=False,
        )

        return process.returncode == 0
