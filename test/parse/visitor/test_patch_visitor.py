from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pytest import raises

from flash_patcher.antlr_source.PatchfileLexer import PatchfileLexer
from flash_patcher.antlr_source.PatchfileParser import PatchfileParser

from flash_patcher.exception.injection import InjectionError
from flash_patcher.inject.bulk_injection import BulkInjectionManager
from flash_patcher.parse.common import CommonParseManager
from flash_patcher.parse.visitor.patch_visitor import PatchfileProcessor

# pylint: disable=wrong-import-order
from test.test_util.get_patch_context import get_remove_patch_context

class PatchfileProcessorSpec (TestCase):

    add_context: PatchfileParser.AddBlockContext
    remove_context: PatchfileParser.RemoveBlockContext
    replace_nth_context: PatchfileParser.ReplaceNthBlockContext
    root_context: PatchfileParser.RootContext

    replace_all_root_context: PatchfileParser.RootContext

    mock_injector: MagicMock[BulkInjectionManager]
    patch_visitor: PatchfileProcessor

    def __init__(self: PatchfileProcessorSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.patch_visitor = PatchfileProcessor(
            Path("../test/testdata/Patch1.patch"),
            Path("../"),
            Path(".Patcher-Temp/"),
            Path("../test/testdata/"),
        )

        self.mock_injector = MagicMock()
        self.patch_visitor.injector = self.mock_injector

        self.root_context = CommonParseManager(PatchfileLexer, PatchfileParser).get_root(
            Path("../test/testdata/Patch1.patch")
        )

        self.add_context = self.root_context.addBlock()[0]
        self.remove_context = self.root_context.removeBlock()[0]
        self.replace_nth_context = self.root_context.replaceNthBlock()[0]

        self.replace_all_root_context = CommonParseManager(PatchfileLexer, PatchfileParser) \
            .get_root(Path("../test/testdata/Patch4.patch"))

    def test_visit_add_block_success(self: PatchfileProcessorSpec) -> None:
        self.patch_visitor.visitAddBlock(self.add_context)

        assert self.mock_injector.add_injection_target.call_count == 7

        self.mock_injector.inject.assert_called_once_with(
            "// This is an actionscript command\n" \
            "This is not an actionscript command, it's just invalid\n" \
            "// cmd: skip 20\n"
        )

        assert len(self.patch_visitor.modified_scripts) == 1

    # Overwriting write is super annoying...
    # (For some reason patching writelines_safe doesn't work)
    @patch('pathlib.Path.open', create=True)
    def test_visit_remove_block_success(
        self: PatchfileProcessorSpec,
        mock_open: MagicMock,
    ) -> None:
        mock_file = MagicMock()

        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.readlines.return_value = [" "] * 100

        with patch.object(mock_file, 'writelines') as mock_writelines:
            self.patch_visitor.visitRemoveBlock(self.remove_context)

            mock_writelines.assert_called_once()

        assert len(self.patch_visitor.modified_scripts) == 1

    @patch('flash_patcher.inject.single_injection.SingleInjectionManager.inject')
    def test_visit_replace_nth_block_success(
        self: PatchfileProcessorSpec,
        mock_single_injector: MagicMock,
    ) -> None:
        self.patch_visitor.visitReplaceNthBlock(self.replace_nth_context)

        assert mock_single_injector.call_count == 3

        assert len(self.patch_visitor.modified_scripts) == 1

    @patch('pathlib.Path.open', create=True)
    def test_visit_replace_all_block_multiple_replacement(
        self: PatchfileProcessorSpec,
        mock_open: MagicMock,
    ) -> None:
        mock_file = MagicMock()

        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.read.return_value = "testtesttest"

        with patch.object(mock_file, 'writelines') as mock_writelines:
            self.patch_visitor.visitReplaceAllBlock(
                self.replace_all_root_context.replaceAllBlock(1)
            )

            mock_writelines.assert_called_once_with([
                "// some content// some content// some content"
            ])

    @patch('pathlib.Path.open', create=True)
    def test_visit_replace_all_block_none(
        self: PatchfileProcessorSpec,
        mock_open: MagicMock,
    ) -> None:
        mock_file = MagicMock()

        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.read.return_value = "testtesttest"

        with patch.object(mock_file, 'writelines') as mock_writelines:
            self.patch_visitor.visitReplaceAllBlock(
                self.replace_all_root_context.replaceAllBlock(0)
            )

            mock_writelines.assert_called_once_with(["testtesttest"])

    # Overwriting write is super annoying...
    # (For some reason patching writelines_safe doesn't work)
    @patch('pathlib.Path.open', create=True)
    def test_visit_remove_block_failure_beyond_eof(
        self: PatchfileProcessorSpec,
        mock_open: MagicMock,
    ) -> None:
        mock_file = MagicMock()

        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.readlines.return_value = [" "] * 2

        with raises(InjectionError):
            self.patch_visitor.visitRemoveBlock(self.remove_context)

    def test_visit_remove_block_failure_invalid_target(
        self: PatchfileProcessorSpec,
    ) -> None:
        context = get_remove_patch_context(
            Path("../test/testdata/Patch1.patch"), 1,
        )

        with raises(InjectionError):
            self.patch_visitor.visitRemoveBlock(context)

    @patch('shutil.copyfile')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    def test_visit_add_asset_block_success_no_folder(
        self: PatchfileProcessorSpec,
        mock_path_exists: MagicMock,
        mock_path_mkdir: MagicMock,
        mock_shutil_copyfile: MagicMock,
    ) -> None:
        root_context = CommonParseManager(PatchfileLexer, PatchfileParser).get_root(
            Path("../test/testdata/Pack1.assets")
        )

        mock_path_exists.side_effect = [True, False]

        self.patch_visitor.visitRoot(root_context)

        mock_path_mkdir.assert_called_once_with(
            Path(".Patcher-Temp/images")
        )
        mock_shutil_copyfile.assert_called_once_with(
            Path("../local.png"), Path(".Patcher-Temp/images/18.png")
        )

        assert self.patch_visitor.modified_scripts == set([
            Path(".Patcher-Temp/images/18.png")
        ])

    @patch('shutil.copyfile')
    @patch('pathlib.Path.exists')
    def test_visit_add_asset_block_success_with_folder(
        self: PatchfileProcessorSpec,
        mock_path_exists: MagicMock,
        mock_shutil_copyfile: MagicMock,
    ) -> None:
        root_context = CommonParseManager(PatchfileLexer, PatchfileParser).get_root(
            Path("../test/testdata/Pack1.assets")
        )

        mock_path_exists.return_value = True

        self.patch_visitor.visitRoot(root_context)

        mock_shutil_copyfile.assert_called_once_with(
            Path("../local.png"), Path(".Patcher-Temp/images/18.png")
        )

        assert self.patch_visitor.modified_scripts == set([
            Path(".Patcher-Temp/images/18.png")
        ])

    @patch('pathlib.Path.exists')
    def test_visit_add_asset_block_failure_not_exists(
        self: PatchfileProcessorSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        root_context = CommonParseManager(PatchfileLexer, PatchfileParser).get_root(
            Path("../test/testdata/Pack1.assets")
        )

        mock_path_exists.return_value = False

        with raises(FileNotFoundError):
            self.patch_visitor.visitRoot(root_context)

    @patch('flash_patcher.parse.visitor.patch_visitor.PatchfileProcessor.visitRemoveBlock')
    @patch('flash_patcher.parse.visitor.patch_visitor.PatchfileProcessor.visitAddBlock')
    def test_visit_root(
        self: PatchfileProcessorSpec,
        mock_visit_add: MagicMock,
        mock_visit_remove: MagicMock,
    ) -> None:
        self.patch_visitor.visitRoot(self.root_context)

        mock_visit_add.assert_called_once_with(self.add_context)

        assert mock_visit_remove.call_count == 2
