from __future__ import annotations

import base64
from pathlib import Path

from flash_patcher.compile.ffdec import FFDecInterface
from flash_patcher.exception.dependency import DependencyError
from flash_patcher.util.logging import logger

class CompilationManager:
    """Manage Flash compilation and decompilation, including caching.

    This class should not call FFDec directly, instead it should use the FFDecInterface.
    """

    decompiler: FFDecInterface

    def __init__(self: CompilationManager) -> None:
        self.decompiler = FFDecInterface()

    def decompile(
        self: CompilationManager,
        inputfile: Path,
        drop_cache: bool = False,
        xml_mode: bool = False
    ) -> Path:
        """Decompile the SWF and return the decompilation location.

        This uses caching to save time.

        inputfile: the SWF to decompile
        drop_cache: if True, will force decompilation instead of using cached files
        xml_mode: if True, will dump XML instead of decompiling normally
        """
        # Validity checking: Decompilation path and input file
        if not Path("./.Patcher-Temp").exists():
            Path("./.Patcher-Temp").mkdir()

        if not inputfile.exists():
            failure_mesg = f"""Could not locate the SWF file: {inputfile}.
            Aborting..."""

            logger.error(failure_mesg)
            raise FileNotFoundError(failure_mesg)

        # Decompile swf into temp folder called ./.Patcher-Temp/[swf name, base32 encoded]
        cache_location = Path(
            "./.Patcher-Temp/",
            base64.b32encode(
                bytes(inputfile.name, "utf-8"),
            ).decode("ascii"),
        )

        # If the cache is dropped or nonexistent, rerun decompiler
        if drop_cache or (not Path(cache_location).exists()):
            if not Path(cache_location).exists() and not xml_mode:
                Path(cache_location).mkdir()

            logger.info("Beginning decompilation...")

            decomp = None

            if xml_mode:
                decomp = self.decompiler.dump_xml(inputfile, cache_location)
                logger.info("XML decompilation mode.")
            else:
                decomp = self.decompiler.export_scripts(inputfile, cache_location)

            if not decomp:
                failure_mesg = f"""FFDec couldn't decompile the SWF file: {inputfile}.
                    Aborting..."""

                logger.error(failure_mesg)
                raise DependencyError(failure_mesg)

        else:
            logger.info("Detected cached decompilation. Skipping...")

        return cache_location

    def recompile_with_check(
        self: CompilationManager,
        part: str,
        decomp_location: Path,
        swf: Path,
        output: Path,
    ) -> None:
        """Recompile the SWF part, with a check for program errors."""
        recomp = self.decompiler.recompile_data(part, decomp_location, swf, output)

        if not recomp:
            failure_mesg = f"""FFDec couldn't recompile the SWF file: {swf}.
                Aborting.."""

            logger.error(failure_mesg)
            raise DependencyError(failure_mesg)

    def recompile(
        self: CompilationManager,
        injection: Path,
        inputfile: Path,
        output: Path,
        recompile_all: bool = False,
        xml_mode: bool = False,
    ) -> None:
        """Recompile the SWF after injection is complete.

        inputfile: The base SWF to use for missing files
        outputfile: The location to save the output
        recompile_all: If this is set to False, will only recompile scripts
        """
        if xml_mode:
            self.decompiler.rebuild_xml(injection, output)
            return

        self.recompile_with_check("Script", injection, inputfile, output)

        if recompile_all:
            for part in ("Images", "Sounds", "Shapes", "Text"):
                # FFDec doesn't have a way to import everything at once.
                # We re-import iteratively.
                self.recompile_with_check(part, injection, output, output)
