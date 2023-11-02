from __future__ import annotations

import base64
import sys
from logging import error, info
from pathlib import Path

from .jpexs import JPEXSInterface

class CompilationManager:
    """Manage Flash compilation and decompilation, including caching.

    This class should not call JPEXS directly, instead it should use the JPEXSInterface.
    """

    decompiler: JPEXSInterface

    def __init__(self: CompilationManager) -> None:
        self.decompiler = JPEXSInterface()

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
            error(
                """Could not locate the SWF file: %s.
                Aborting...""",
                inputfile,
            )
            sys.exit(1)

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

            info("Beginning decompilation...")

            decomp = None

            if xml_mode:
                decomp = self.decompiler.dump_xml(inputfile, cache_location)
                info("XML decompilation mode.")
            else:
                decomp = self.decompiler.export_scripts(inputfile, cache_location)

            if not decomp:
                error(
                    """JPEXS couldn't decompile the SWF file: %s.
                    Aborting...""",
                    inputfile,
                )
                sys.exit(1)

        else:
            info("Detected cached decompilation. Skipping...")

        return cache_location
    
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
        # Repackage the file as a SWF
        # Rant: JPEXS should really return an error code if recompilation fails here!
        # Unable to detect if this was successful or not otherwise.
        if xml_mode:
            self.decompiler.rebuild_xml(injection, output)
            return

        self.decompiler.recompile_data("Script", injection, inputfile, output)

        if recompile_all:
            for part in ("Images", "Sounds", "Shapes", "Text"):
                # JPEXS doesn't have a way to import everything at once.
                # We re-import iteratively.
                self.decompiler.recompile_data(part, injection, output, output)
