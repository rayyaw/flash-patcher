from __future__ import annotations

from pathlib import Path

from flash_patcher.antlr_source.AssetPackLexer import AssetPackLexer
from flash_patcher.antlr_source.AssetPackParser import AssetPackParser

from flash_patcher.parse.common import CommonParseManager
from flash_patcher.parse.visitor.asset_visitor import AssetPackProcessor

class AssetPackManager:
    """Manage asset pack files."""
    asset_pack_processor: AssetPackProcessor
    file: Path

    def __init__(
        self: AssetPackManager,
        folder: Path,
        decomp_location: Path,
        file: Path,
    ) -> None:
        self.asset_pack_processor = AssetPackProcessor(folder, decomp_location)
        self.file = file

    def parse(self: AssetPackManager) -> set:
        """Parse a single asset pack.
        
        This class handles everything to do with preprocessing (opening the file, etc.)
        Everything within the file will be handled by the AssetPackProcessor
        """
        asset_pack = CommonParseManager(AssetPackLexer, AssetPackParser).get_root(self.file)

        return self.asset_pack_processor.visitRoot(asset_pack)
