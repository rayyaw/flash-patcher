from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.compile.compilation import CompilationManager
from src.compile.jpexs import JPEXSInterface

class CompilationManagerSpec (TestCase):

    mock_decompiler : MagicMock
    compilation_manager: CompilationManager

    swf: Path
    input_folder: Path
    output_folder: Path

    def __init__(self: CompilationManagerSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        # Manual initialization required to mock the internal JPEXS interface
        self.compilation_manager = CompilationManager()
        self.compilation_manager.decompiler = MagicMock(spec=JPEXSInterface)

        self.swf = Path("test.swf")
        self.input_folder = Path("./.Patcher-Temp/mod")
        self.output_folder = Path("./.Patcher-Temp/SMF")


    @patch('pathlib.Path.exists')
    def test_decompile_no_input(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.return_value = False
        self.compilation_manager.decompile(self.swf)

        mock_path_exists.assert_called_once_with(self.swf)


