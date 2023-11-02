from __future__ import annotations

from antlr_source.StagefileParser import StagefileParser
from antlr_source.StagefileVisitor import StagefileVisitor
from pathlib import Path

from parse.asset import AssetPackManager
from parse.patch import PatchfileManager

class StagefileProcessor (StagefileVisitor):

    folder: Path                    # Folder the patch files are in
    decompLocation: Path            # Decomp location of SWF
    decompLocationWithScripts: Path # Decomp location of SWF scripts
    modifiedScripts: set            # Set of scripts that were modified (and need to be recompiled)

    def __init__(
        self: StagefileProcessor,
        folder: Path,
        decomp_location: Path,
        decomp_location_with_scripts: Path
     ) -> None:
        self.decompLocation = decomp_location
        self.decompLocationWithScripts = decomp_location_with_scripts
        self.folder = folder

        self.modifiedScripts = set()

    def visitPatchFile(self: StagefileProcessor, ctx: StagefileParser.PatchFileContext) -> None:
        self.modifiedScripts |= PatchfileManager.parse(
            self.decompLocationWithScripts, 
            self.folder / ctx.getText()
        )

    def visitAssetPackFile(self: StagefileProcessor, ctx: StagefileParser.AssetPackFileContext) -> None:
         # TODO once asset packs are completed
        self.modifiedScripts |= AssetPackManager.parse(
            self.decompLocation,
            self.folder / ctx.getText()
        )
    
    def visitRoot(self, ctx: StagefileParser.RootContext) -> set:
        super().visitRoot(ctx)
        return self.modifiedScripts