from __future__ import annotations

import shutil
from logging import exception
from pathlib import Path

from flash_patcher.antlr_source.AssetPackParser import AssetPackParser
from flash_patcher.antlr_source.AssetPackVisitor import AssetPackVisitor

class AssetPackProcessor (AssetPackVisitor):
    """This class inherits from the ANTLR visitor to process asset pack files.
    
    It will automatically take in the file syntax tree and add the files to the SWF.
    """

    asset_folder: Path
    decomp_location: Path
    modified_scripts: set[Path]

    def __init__(self: AssetPackProcessor, asset_folder: Path, decomp_location: Path) -> None:
        self.asset_folder = asset_folder
        self.decomp_location = decomp_location
        self.modified_scripts = set()

    def visitAddAssetBlock(self, ctx: AssetPackParser.AddAssetBlockContext) -> None:
        """In an Add Asset block, we should take the specified assets and copy them into the SWF"""
        local_name = ctx.local.getText()
        remote_name = ctx.swf.getText()

        if not Path(self.asset_folder / local_name).exists():
            error_mesg = f"""Could not find asset: {local_name}
            Aborting..."""
            exception(error_mesg)
            raise FileNotFoundError(error_mesg)

        # Create folder and copy things over
        remote_folder = remote_name.split("/")[0]

        if not (self.decomp_location / remote_folder).exists():
            Path.mkdir(self.decomp_location / remote_folder)

        shutil.copyfile(self.asset_folder / local_name, self.decomp_location / remote_name)

        self.modified_scripts.add(self.decomp_location / remote_name)

    def visitRoot(self, ctx: AssetPackParser.RootContext) -> set:
        """Root function. Call this when running the visitor."""
        super().visitRoot(ctx)
        return self.modified_scripts
