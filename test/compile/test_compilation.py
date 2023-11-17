from __future__ import annotations

import sys
import os
from pathlib import Path
from pytest import raises
from unittest import TestCase
from unittest.mock import MagicMock, patch

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from compile.compilation import CompilationManager
from compile.jpexs import JPEXSInterface
from exception.dependency import DependencyError

class CompilationManagerSpec (TestCase):

    mock_decompiler: MagicMock
    compilation_manager: CompilationManager

    swf: Path
    input_folder: Path
    output_folder: Path

    def __init__(self: CompilationManagerSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        # Manual initialization required to mock the internal JPEXS interface
        self.compilation_manager = CompilationManager()
        self.mock_decompiler = MagicMock(spec=JPEXSInterface)
        self.compilation_manager.decompiler = self.mock_decompiler

        self.swf = Path("test.swf")
        self.input_folder = Path("./.Patcher-Temp/mod")
        self.output_folder = Path("./.Patcher-Temp/SMF")

    @patch('pathlib.Path.exists')
    def test_decompile_success_xml_mode(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.return_value = True

        self.compilation_manager.decompile(self.swf, drop_cache=True, xml_mode=True)

        assert mock_path_exists.call_count == 3
        self.mock_decompiler.dump_xml.assert_called_once_with(
            self.swf, Path('.Patcher-Temp/ORSXG5BOON3WM===')
        )

    @patch('pathlib.Path.exists')
    def test_decompile_success_no_cache(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.side_effect = [True, True, False, True]

        self.compilation_manager.decompile(self.swf)

        assert mock_path_exists.call_count == 4
        self.mock_decompiler.export_scripts.assert_called_once_with(
            self.swf, Path('.Patcher-Temp/ORSXG5BOON3WM===')
        )

    @patch('pathlib.Path.exists')
    def test_decompile_success_drop_cache(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.return_value = True

        self.compilation_manager.decompile(self.swf, drop_cache=True)

        assert mock_path_exists.call_count == 3
        self.mock_decompiler.export_scripts.assert_called_once_with(
            self.swf, Path('.Patcher-Temp/ORSXG5BOON3WM===')
        )

    @patch('pathlib.Path.exists')
    def test_decompile_success_cached(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.return_value = True

        self.compilation_manager.decompile(self.swf)

        assert mock_path_exists.call_count == 3
        self.mock_decompiler.assert_not_called()

    @patch('pathlib.Path.exists')
    def test_decompile_failure_no_input(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.side_effect = [True, False]

        with raises(FileNotFoundError):
            self.compilation_manager.decompile(self.swf)

        assert mock_path_exists.call_count == 2
        self.mock_decompiler.assert_not_called()

    @patch('pathlib.Path.exists')
    def test_decompile_failure_jpexs_error(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.return_value = True
        self.mock_decompiler.export_scripts.return_value = False

        with raises(DependencyError):
            self.compilation_manager.decompile(self.swf, drop_cache=True)

        assert mock_path_exists.call_count == 3
        self.mock_decompiler.export_scripts.assert_called_once_with(
            self.swf, Path('.Patcher-Temp/ORSXG5BOON3WM===')
        )

# FIXME - insert all tests for recompilation here
