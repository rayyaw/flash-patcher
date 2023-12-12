from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pytest import raises

from flash_patcher.antlr_source.PatchfileLexer import PatchfileLexer
from flash_patcher.antlr_source.PatchfileParser import PatchfileParser
from flash_patcher.exception_handle.dependency import DependencyError
from flash_patcher.parse.common import CommonParseManager

class CommonParseManagerSpec (TestCase):

    common_parse_manager: CommonParseManager
    patch_file: Path

    def __init__(self: CommonParseManagerSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.common_parse_manager = CommonParseManager(PatchfileLexer, PatchfileParser)
        self.patch_file = Path("../test/testdata/Patch1.patch")

    def test_parse_input_sucess(
        self: CommonParseManagerSpec,
    ) -> None:
        with self.patch_file.open(encoding="utf-8") as file:
            content = file.read()

        parse_tree = self.common_parse_manager.parse_input(content).root()

        assert len(parse_tree.addBlock()) == 1
        assert len(parse_tree.removeBlock()) == 2

        # ANTLR parse contexts will strip spaces for the getText() method
        assert parse_tree.addBlock()[0].getText().startswith("addframe_1/DoAction")
        assert parse_tree.addBlock()[0].getText().endswith("end-patch")

    def test_get_root_success(
        self: CommonParseManagerSpec,
    ) -> None:
        parse_tree = self.common_parse_manager.get_root(self.patch_file)

        assert len(parse_tree.addBlock()) == 1
        assert len(parse_tree.removeBlock()) == 2

        # ANTLR parse contexts will strip spaces for the getText() method
        assert parse_tree.addBlock()[0].getText().startswith("addframe_1/DoAction")
        assert parse_tree.addBlock()[0].getText().endswith("end-patch")

    @patch('flash_patcher.parse.common.CommonParseManager.parse_input')
    def test_get_root_failure_parse_exception(
        self: CommonParseManagerSpec,
        mock_parse_input: MagicMock,
    ) -> None:

        mock_parse_input.return_value = "this is not callable!!"

        with raises(DependencyError):
            self.common_parse_manager.get_root(self.patch_file)
