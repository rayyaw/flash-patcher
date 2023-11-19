from __future__ import annotations

import sys
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from parse.asset import AssetPackManager
from parse.visitor.asset_visitor import AssetPackProcessor

class AssetPackManagerSpec (TestCase):

    mock_processor: MagicMock[AssetPackProcessor]
    asset_pack_manager: AssetPackManager

    def __init__(self: AssetPackManagerSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.mock_processor = MagicMock(AssetPackProcessor)

        self.asset_pack_manager = AssetPackManager(
            Path("../"),
            Path("./.Patcher-Temp"),
        )

        self.asset_pack_manager.asset_pack_processor = self.mock_processor

    def test_parse_success(
        self: AssetPackManagerSpec,
    ) -> None:
        self.asset_pack_manager.parse(
            Path("../test/testdata/Pack1.assets"),
        )

        self.mock_processor.visitRoot.assert_called_once()

