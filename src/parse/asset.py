from __future__ import annotations

from pathlib import Path

from antlr_source.AssetPackLexer import AssetPackLexer
from antlr_source.AssetPackParser import AssetPackParser

from parse.common import CommonParseManager
from parse.visitor.asset_visitor import AssetPackProcessor

class AssetPackManager:
    """Manage asset pack files."""
    asset_pack_processor: AssetPackProcessor

    def __init__(self: AssetPackManager, folder: Path, decomp_location: Path) -> None:
        self.asset_pack_processor = AssetPackProcessor(folder, decomp_location)

    def parse(
        self: AssetPackManager,
        file: Path
    ) -> set:
        """Parse a single asset pack.
        
        This class handles everything to do with preprocessing (opening the file, etc.)
        Everything within the file will be handled by the AssetPackProcessor
        """
        asset_pack = CommonParseManager.get_root(AssetPackLexer, AssetPackParser, file)

        return self.asset_pack_processor.visitRoot(asset_pack)
