from __future__ import annotations

from pathlib import Path

from flash_patcher.antlr_source.PatchfileLexer import PatchfileLexer
from flash_patcher.antlr_source.PatchfileParser import PatchfileParser

from flash_patcher.parse.common import CommonParseManager
from flash_patcher.parse.visitor.patch_visitor import PatchfileProcessor

class PatchfileManager:
    """Manage patch files."""

    file: Path
    patchfile_processor: PatchfileProcessor

    def __init__(self: PatchfileManager, decomp_location: Path, file: Path) -> None:
        self.file = file
        self.patchfile_processor = PatchfileProcessor(self.file, decomp_location)

    def parse(self: PatchfileManager) -> set:
        """Parse a single patch file.

        folder_location: The location of the decompiled scripts from the SWF.
        file_location: The location of the patch file to apply.
        
        This class handles everything to do with preprocessing (opening the file, etc.)
        Everything within the file will be handled by the PatchfileProcessor
        Return the set of modified scripts.
        """
        patchfile = CommonParseManager(PatchfileLexer, PatchfileParser).get_root(self.file)

        return self.patchfile_processor.visitRoot(patchfile)
