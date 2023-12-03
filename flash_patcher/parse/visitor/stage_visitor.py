from __future__ import annotations

from pathlib import Path

from flash_patcher.antlr_source.StagefileParser import StagefileParser
from flash_patcher.antlr_source.StagefileVisitor import StagefileVisitor

from flash_patcher.parse.asset import AssetPackManager
from flash_patcher.parse.patch import PatchfileManager

class StagefileProcessor (StagefileVisitor):
    """This class inherits from the ANTLR visitor to process stage files.
    
    It will automatically take in the file syntax tree 
    and perform all injections and asset adds in it.
    """

    # Folder the patch files are in
    folder: Path

    # Decomp location of SWF
    decomp_location: Path

    # Decomp location of SWF scripts
    decomp_location_with_scripts: Path

    # Set of scripts that were modified and need recompilation
    modified_scripts: set[Path]

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
        """When we encounter a patch file, we should open and process it"""
        self.modified_scripts |= PatchfileManager(
            self.decomp_location_with_scripts, self.folder / ctx.getText()
        ).parse()

    def visitAssetPackFile(
        self: StagefileProcessor,
        ctx: StagefileParser.AssetPackFileContext
    ) -> None:
        """When we encounter an asset pack, we should open and process it"""
        self.modified_scripts |= AssetPackManager(
            self.folder, self.decomp_location, self.folder / ctx.getText()
        ).parse()

    def visitRoot(self: StagefileProcessor, ctx: StagefileParser.RootContext) -> set:
        """Root function. Call this when running the visitor."""
        super().visitRoot(ctx)
        return self.modified_scripts
