from __future__ import annotations

import sys
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from antlr_source.StagefileLexer import StagefileLexer
from antlr_source.StagefileParser import StagefileParser
from parse.common import CommonParseManager
from parse.visitor.stage_visitor import StagefileProcessor

class StagefileProcessorSpec (TestCase):

    asset_pack_context: StagefileParser.AssetPackFileContext
    patchfile_context: StagefileParser.PatchFileContext
    root_context: StagefileParser.RootContext

    stage_processor: StagefileProcessor

    def __init__(self: StagefileProcessorSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.root_context = CommonParseManager(
            StagefileLexer, StagefileParser
        ).get_root(Path("../test/testdata/Stage1.stage"))

        self.asset_pack_context = self.root_context.assetPackFile()[0]
        self.patchfile_context = self.root_context.patchFile()[0]

        self.stage_processor = StagefileProcessor(
            Path("../test/testdata/"),
            Path("./.Patcher-Temp/mod"),
            Path("./.Patcher-Temp/mod/scripts"),
        )

    @patch('parse.visitor.stage_visitor.StagefileProcessor.visitPatchFile')
    @patch('parse.visitor.stage_visitor.StagefileProcessor.visitAssetPackFile')
    def test_visit_root_success(
        self: StagefileProcessorSpec,
        mock_asset_visit: MagicMock,
        mock_patch_visit: MagicMock,
    ) -> None:
        self.stage_processor.visitRoot(self.root_context)

        mock_asset_visit.assert_called_once_with(self.asset_pack_context)
        mock_patch_visit.assert_called_once_with(self.patchfile_context)

    @patch('parse.asset.AssetPackManager.parse')
    def test_visit_add_asset_pack_success(
        self: StagefileProcessorSpec,
        mock_parse_asset_pack: MagicMock,
    ) -> None:
        self.stage_processor.visitAssetPackFile(self.asset_pack_context)

        mock_parse_asset_pack.assert_called_once_with()

    @patch('parse.patch.PatchfileManager.parse')
    def test_visit_patchfile_success(
        self: StagefileProcessorSpec,
        mock_parse_patchfile: MagicMock,
    ) -> None:
        self.stage_processor.visitPatchFile(self.patchfile_context)

        mock_parse_patchfile.assert_called_once_with()
