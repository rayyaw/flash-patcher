from __future__ import annotations

import sys
import shutil
from antlr_source.AssetPackParser import AssetPackParser
from antlr_source.AssetPackVisitor import AssetPackVisitor
from logging import exception
from pathlib import Path

class AssetPackProcessor (AssetPackVisitor):

    decompLocation: Path
    modifiedScripts: set

    def __init__(self: AssetPackProcessor, asset_folder: Path, decomp_location: Path) -> None:
        self.assetFolder = asset_folder
        self.decompLocation = decomp_location
        self.modifiedScripts = set()

    def visitAddAssetBlock(self, ctx: AssetPackParser.AddAssetBlockContext) -> None:
        local_name = ctx.local.getText()
        remote_name = ctx.swf.getText()

        if not Path(self.assetFolder / local_name).exists():
            exception(
                """Could not find asset: %s
                Aborting...""",
                local_name,
            )
            sys.exit(1)

        # Create folder and copy things over
        remote_folder = remote_name.split("/")[0]

        if not (self.decompLocation / remote_folder).exists():
            Path.mkdir(self.decompLocation / remote_folder)

        shutil.copyfile(self.assetFolder / local_name, self.decompLocation / remote_name)

        self.modifiedScripts.add(self.decompLocation / remote_name)


    def visitRoot(self, ctx: AssetPackParser.RootContext) -> set:
        super().visitRoot(ctx)
        return self.modifiedScripts