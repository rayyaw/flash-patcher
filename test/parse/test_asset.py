from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

from flash_patcher.parse.asset import AssetPackManager
from flash_patcher.parse.visitor.asset_visitor import AssetPackProcessor

class AssetPackManagerSpec (TestCase):

    mock_processor: MagicMock[AssetPackProcessor]
    asset_pack_manager: AssetPackManager

    def __init__(self: AssetPackManagerSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.mock_processor = MagicMock(AssetPackProcessor)

        self.asset_pack_manager = AssetPackManager(
            Path("../"),
            Path("./.Patcher-Temp"),
            Path("../test/testdata/Pack1.assets"),
        )

        self.asset_pack_manager.asset_pack_processor = self.mock_processor

    def test_parse_success(
        self: AssetPackManagerSpec,
    ) -> None:
        self.asset_pack_manager.parse()

        self.mock_processor.visitRoot.assert_called_once()
