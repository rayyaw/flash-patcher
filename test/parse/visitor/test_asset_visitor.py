from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pytest import raises

from flash_patcher.antlr_source.AssetPackLexer import AssetPackLexer
from flash_patcher.antlr_source.AssetPackParser import AssetPackParser
from flash_patcher.parse.common import CommonParseManager
from flash_patcher.parse.visitor.asset_visitor import AssetPackProcessor

class AssetPackVisitorSpec (TestCase):

    add_asset_block_context: AssetPackParser.AddAssetBlockContext
    root_context: AssetPackParser.RootContext
    asset_pack_visitor: AssetPackProcessor

    def __init__(self: AssetPackVisitorSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.asset_pack_visitor = AssetPackProcessor(
            Path("../"),
            Path("./.Patcher-Temp/")
        )

        self.root_context = CommonParseManager(AssetPackLexer, AssetPackParser).get_root(
            Path("../test/testdata/Pack1.assets")
        )

        self.add_asset_block_context = self.root_context.addAssetBlock()[0]

    @patch('shutil.copyfile')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    def test_visit_add_asset_block_success_no_folder(
        self: AssetPackVisitorSpec,
        mock_path_exists: MagicMock,
        mock_path_mkdir: MagicMock,
        mock_shutil_copyfile: MagicMock,
    ) -> None:
        mock_path_exists.side_effect = [True, False]

        self.asset_pack_visitor.visitRoot(self.root_context)

        mock_path_mkdir.assert_called_once_with(
            Path(".Patcher-Temp/images")
        )
        mock_shutil_copyfile.assert_called_once_with(
            Path("../local.png"), Path(".Patcher-Temp/images/18.png")
        )

        assert self.asset_pack_visitor.modified_scripts == set([
            Path(".Patcher-Temp/images/18.png")
        ])

    @patch('shutil.copyfile')
    @patch('pathlib.Path.exists')
    def test_visit_add_asset_block_success_with_folder(
        self: AssetPackVisitorSpec,
        mock_path_exists: MagicMock,
        mock_shutil_copyfile: MagicMock,
    ) -> None:
        mock_path_exists.return_value = True

        self.asset_pack_visitor.visitRoot(self.root_context)

        mock_shutil_copyfile.assert_called_once_with(
            Path("../local.png"), Path(".Patcher-Temp/images/18.png")
        )

        assert self.asset_pack_visitor.modified_scripts == set([
            Path(".Patcher-Temp/images/18.png")
        ])

    @patch('pathlib.Path.exists')
    def test_visit_add_asset_block_failure_not_exists(
        self: AssetPackVisitorSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.return_value = False

        with raises(FileNotFoundError):
            self.asset_pack_visitor.visitRoot(self.root_context)

    @patch('flash_patcher.parse.visitor.asset_visitor.AssetPackProcessor.visitAddAssetBlock')
    def test_visit_root_context_success(
        self: AssetPackVisitorSpec,
        mock_visit_add: MagicMock,
    ) -> None:
        self.asset_pack_visitor.visitRoot(self.root_context)

        assert mock_visit_add.call_count == 1
