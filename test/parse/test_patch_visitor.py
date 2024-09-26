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
from flash_patcher.parse.patch_visitor import PatchfileProcessor
from flash_patcher.parse.scope import Scope

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
            Path("../test/testdata/"),
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

        mock_path_exists.side_effect = [True, False, True, False]

        self.patch_visitor.visitRoot(root_context)

        assert mock_path_mkdir.call_count == 2
        assert mock_path_mkdir.call_args_list[0].args == (Path(".Patcher-Temp/images"),)
        assert mock_path_mkdir.call_args_list[1].args == (Path(".Patcher-Temp/images"),)

        assert mock_shutil_copyfile.call_count == 2
        assert mock_shutil_copyfile.call_args_list[0].args == (
            Path("../test/testdata/local.png"), Path(".Patcher-Temp/images/18.png")
        )
        assert mock_shutil_copyfile.call_args_list[1].args == (
            Path("../test/testdata/space -dash.png"), Path(".Patcher-Temp/images/space -dash.png")
        )

        assert self.patch_visitor.modified_scripts == set([
            Path(".Patcher-Temp/images/18.png"),
            Path(".Patcher-Temp/images/space -dash.png")
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

        assert mock_shutil_copyfile.call_count == 2
        assert mock_shutil_copyfile.call_args_list[0].args == (
            Path("../test/testdata/local.png"), Path(".Patcher-Temp/images/18.png")
        )
        assert mock_shutil_copyfile.call_args_list[1].args == (
            Path("../test/testdata/space -dash.png"), Path(".Patcher-Temp/images/space -dash.png")
        )

        assert self.patch_visitor.modified_scripts == set([
            Path(".Patcher-Temp/images/18.png"),
            Path(".Patcher-Temp/images/space -dash.png")
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

    def test_visit_set_var(self: PatchfileProcessorSpec) -> None:
        self.patch_visitor.visitSetVarBlock(self.root_context.setVarBlock(0))

        assert self.patch_visitor.scope.resolve("key1") == "val1"

    def test_visit_export_var(self: PatchfileProcessorSpec) -> None:
        self.patch_visitor.visitExportVarBlock(self.root_context.exportVarBlock(0))

        assert self.patch_visitor.scope.resolve("key2") == "val2"
        assert Scope().resolve("key2") == "val2"

    @patch("builtins.input")
    def test_visit_python_file_success(
        self: PatchfileProcessorSpec,
        mock_input: MagicMock,
    ) -> None:
        mock_input.return_value = "y"
        self.patch_visitor.decomp_location = Path(".")

        root_context = CommonParseManager(
            PatchfileLexer, PatchfileParser
        ).get_root(Path("../test/testdata/Stage1.stage"))

        python_file_context = root_context.execPythonBlock(0)
        self.patch_visitor.visitExecPythonBlock(python_file_context)

        assert self.patch_visitor.modified_scripts == set([
            Path("DoAction1.as"),
            Path("DoAction2.as")
        ])

    @patch("builtins.input")
    def test_visit_python_file_success_empty(
        self: PatchfileProcessorSpec,
        mock_input: MagicMock,
    ) -> None:
        mock_input.return_value = "y"
        self.patch_visitor.decomp_location = Path(".")

        root_context = CommonParseManager(
            PatchfileLexer, PatchfileParser
        ).get_root(Path("../test/testdata/Stage1.stage"))

        self.patch_visitor.visitExecPythonBlock(root_context.execPythonBlock(1))

        # implicit assert nothrows
        assert self.patch_visitor.modified_scripts == set()

    @patch('flash_patcher.parse.patch.PatchfileManager.parse')
    def test_visit_patchfile_success(
        self: PatchfileProcessorSpec,
        mock_parse_patchfile: MagicMock,
    ) -> None:
        root_context = CommonParseManager(
            PatchfileLexer, PatchfileParser
        ).get_root(Path("../test/testdata/Stage1.stage"))

        patchfile_context = root_context.execPatcherBlock(0)

        self.patch_visitor.visitExecPatcherBlock(patchfile_context)

        mock_parse_patchfile.assert_called_once_with()

    @patch('flash_patcher.parse.patch_visitor.PatchfileProcessor.visitRemoveBlock')
    @patch('flash_patcher.parse.patch_visitor.PatchfileProcessor.visitAddBlock')
    def test_visit_root(
        self: PatchfileProcessorSpec,
        mock_visit_add: MagicMock,
        mock_visit_remove: MagicMock,
    ) -> None:
        self.patch_visitor.visitRoot(self.root_context)

        mock_visit_add.assert_called_once_with(self.add_context)

        assert mock_visit_remove.call_count == 2
