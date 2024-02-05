from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from flash_patcher.antlr_source.StagefileLexer import StagefileLexer
from flash_patcher.antlr_source.StagefileParser import StagefileParser
from flash_patcher.parse.common import CommonParseManager
from flash_patcher.parse.visitor.stage_visitor import StagefileProcessor

class StagefileProcessorSpec (TestCase):

    python_file_context: StagefileParser.PythonFileContext
    patchfile_context: StagefileParser.PatchFileContext
    root_context: StagefileParser.RootContext

    stage_processor: StagefileProcessor

    def __init__(self: StagefileProcessorSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.root_context = CommonParseManager(
            StagefileLexer, StagefileParser
        ).get_root(Path("../test/testdata/Stage1.stage"))

        self.python_file_context = self.root_context.pythonFile(0)
        self.patchfile_context = self.root_context.patchFile(0)

        self.stage_processor = StagefileProcessor(
            Path("../test/testdata/"),
            Path("../test/testdata/mod"),
            Path("../test/testdata/mod/scripts"),
        )

    @patch('flash_patcher.parse.visitor.stage_visitor.StagefileProcessor.visitPatchFile')
    @patch('flash_patcher.parse.visitor.stage_visitor.StagefileProcessor.visitPythonFile')
    def test_visit_root_success(
        self: StagefileProcessorSpec,
        mock_python_visit: MagicMock,
        mock_patch_visit: MagicMock,
    ) -> None:
        self.stage_processor.visitRoot(self.root_context)

        assert mock_python_visit.call_count == 2
        mock_python_visit.assert_called_with(self.root_context.pythonFile(1))

        assert mock_patch_visit.call_count == 2
        mock_patch_visit.assert_called_with(self.root_context.patchFile(1))

    def test_visit_python_file_success(
        self: StagefileProcessorSpec,
    ) -> None:
        self.stage_processor.visitPythonFile(self.python_file_context)

        assert self.stage_processor.modified_scripts == set([
            Path(".Patcher-Temp/mod/DoAction1.as"),
            Path(".Patcher-Temp/mod/DoAction2.as")
        ])

    def test_visit_python_file_success_empty(
        self: StagefileProcessorSpec,
    ) -> None:
        self.stage_processor.visitPythonFile(self.root_context.pythonFile()[1])

        # implicit assert nothrows
        assert self.stage_processor.modified_scripts == set()

    @patch('flash_patcher.parse.patch.PatchfileManager.parse')
    def test_visit_patchfile_success(
        self: StagefileProcessorSpec,
        mock_parse_patchfile: MagicMock,
    ) -> None:
        self.stage_processor.visitPatchFile(self.patchfile_context)

        mock_parse_patchfile.assert_called_once_with()
