from __future__ import annotations

from pathlib import Path

from antlr_source.StagefileParser import StagefileParser
from antlr_source.StagefileVisitor import StagefileVisitor

from parse.asset import AssetPackManager
from parse.patch import PatchfileManager

class StagefileProcessor (StagefileVisitor):
    """This class inherits from the ANTLR visitor to process stage files.
    
    It will automatically take in the file syntax tree 
    and perform all injections and asset adds in it.
    """

    folder: Path                        # Folder the patch files are in
    decomp_location: Path               # Decomp location of SWF
    decomp_location_with_scripts: Path  # Decomp location of SWF scripts
    modified_scripts: set               # Set of scripts that were modified (need recompilation)

    def __init__(
        self: StagefileProcessor,
        folder: Path,
        decomp_location: Path,
        decomp_location_with_scripts: Path
     ) -> None:
        self.decomp_location = decomp_location
        self.decomp_location_with_scripts = decomp_location_with_scripts
        self.folder = folder

        self.modified_scripts = set()

    def visitPatchFile(
        self: StagefileProcessor,
        ctx: StagefileParser.PatchFileContext
    ) -> None:
        self.modified_scripts |= PatchfileManager.parse(
            self.decomp_location_with_scripts,
            self.folder / ctx.getText()
        )

    def visitAssetPackFile(
        self: StagefileProcessor,
        ctx: StagefileParser.AssetPackFileContext
    ) -> None:
        self.modified_scripts |= AssetPackManager.parse(
            self.decomp_location,
            self.folder,
            self.folder / ctx.getText()
        )

    def visitRoot(self: StagefileProcessor, ctx: StagefileParser.RootContext) -> set:
        super().visitRoot(ctx)
        return self.modified_scripts