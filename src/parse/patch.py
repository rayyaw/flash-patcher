from __future__ import annotations

from antlr_source.PatchfileLexer import PatchfileLexer
from antlr_source.PatchfileParser import PatchfileParser
from pathlib import Path

from parse.common import CommonParseManager
from parse.visitor.patch_visitor import PatchfileProcessor

class PatchfileManager:
    def parse(decomp_location: Path, file: Path) -> set:
        """Parse a single patch file.

        folder_location: The location of the decompiled scripts from the SWF.
        file_location: The location of the patch file to apply.
        
        This class handles everything to do with preprocessing (opening the file, etc.)
        Everything within the file will be handled by the PatchfileProcessor
        Return the set of modified scripts.
        """
        patchfile = CommonParseManager.getRoot(PatchfileLexer, PatchfileParser, file)
        
        return PatchfileProcessor(file, decomp_location).visitRoot(patchfile)