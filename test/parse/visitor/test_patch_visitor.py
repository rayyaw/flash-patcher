from __future__ import annotations

import sys
import os
from contextlib import ExitStack
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pytest import raises

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from antlr_source.PatchfileLexer import PatchfileLexer
from antlr_source.PatchfileParser import PatchfileParser
from inject.bulk_injection import BulkInjectionManager
from parse.common import CommonParseManager
from parse.visitor.patch_visitor import PatchfileProcessor

class PatchfileProcessorSpec (TestCase):

    add_context: PatchfileParser.AddBlockContext
    remove_context: PatchfileParser.RemoveBlockContext
    root_context: PatchfileParser.RootContext

    mock_injector: MagicMock[BulkInjectionManager]
    patch_visitor: PatchfileProcessor

    def __init__(self: PatchfileProcessorSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.patch_visitor = PatchfileProcessor(
            Path("../test/testdata/Patch1.patch"),
            Path("../test/testdata/"),
        )

        self.mock_injector = MagicMock()
        self.patch_visitor.injector = self.mock_injector

        self.root_context = CommonParseManager(PatchfileLexer, PatchfileParser).get_root(
            Path("../test/testdata/Patch1.patch")
        )

        self.add_context = self.root_context.addBlock()[0]
        self.remove_context = self.root_context.removeBlock()[0]

    def test_visit_add_block_success(self: PatchfileProcessorSpec) -> None:
        self.patch_visitor.visitAddBlock(self.add_context)

        assert self.mock_injector.add_injection_target.call_count == 2

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
        with patch.object(mock_file, 'writelines') as mock_writelines:
            self.patch_visitor.visitRemoveBlock(self.remove_context)

            mock_writelines.assert_called_once()

        assert len(self.patch_visitor.modified_scripts) == 1

    # Overwriting write is super annoying...
    # (For some reason patching writelines_safe doesn't work)
    @patch('pathlib.Path.open', create=True)
    def test_visit_remove_block_failure(
        self: PatchfileProcessorSpec,
        mock_open: MagicMock,
    ) -> None:
        mock_file = MagicMock()

        mock_open.return_value.__enter__.return_value = mock_file

        # Using an ExitStack prevents having to use nested with statements
        with ExitStack() as stack:
            mock_readlines = stack.enter_context(
                patch.object(mock_file, 'readlines')
            )
            stack.enter_context(raises(IndexError))

            mock_readlines.return_value = []
            self.patch_visitor.visitRemoveBlock(self.remove_context)

    @patch('parse.visitor.patch_visitor.PatchfileProcessor.visitRemoveBlock')
    @patch('parse.visitor.patch_visitor.PatchfileProcessor.visitAddBlock')
    def test_visit_root(
        self: PatchfileProcessorSpec,
        mock_visit_add: MagicMock,
        mock_visit_remove: MagicMock,
    ) -> None:
        self.patch_visitor.visitRoot(self.root_context)

        mock_visit_add.assert_called_once_with(self.add_context)
        mock_visit_remove.assert_called_once_with(self.remove_context)
