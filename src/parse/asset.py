from __future__ import annotations

from antlr_source.AssetPackLexer import AssetPackLexer
from antlr_source.AssetPackParser import AssetPackParser
from pathlib import Path

from parse.common import CommonParseManager
from parse.visitor.asset_visitor import AssetPackProcessor

class AssetPackManager:
    def parse(
        decomp_location: Path,
        file: Path
    ) -> set:
        """Parse a single asset pack.
        
        This class handles everything to do with preprocessing (opening the file, etc.)
        Everything within the file will be handled by the AssetPackProcessor
        """
        asset_pack = CommonParseManager.getRoot(AssetPackLexer, AssetPackParser, file)

        return AssetPackProcessor(decomp_location).visitRoot(asset_pack)