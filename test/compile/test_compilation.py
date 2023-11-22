from __future__ import annotations

import sys
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import call, MagicMock, patch

from pytest import raises

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from compile.compilation import CompilationManager
from compile.jpexs import JPEXSInterface
from exception_handle.dependency import DependencyError

class CompilationManagerSpec (TestCase):

    mock_decompiler: MagicMock[JPEXSInterface]
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
        self.folder = Path("./.Patcher-Temp/mod")

    @patch('pathlib.Path.exists')
    def test_decompile_success_xml_mode(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.return_value = True

        folder = self.compilation_manager.decompile(self.swf, drop_cache=True, xml_mode=True)

        assert mock_path_exists.call_count == 3
        assert folder == Path('.Patcher-Temp/ORSXG5BOON3WM===')
        self.mock_decompiler.dump_xml.assert_called_once_with(
            self.swf, Path('.Patcher-Temp/ORSXG5BOON3WM===')
        )

    @patch('pathlib.Path.exists')
    def test_decompile_success_no_cache(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.side_effect = [True, True, False, True]

        folder = self.compilation_manager.decompile(self.swf)

        assert mock_path_exists.call_count == 4
        assert folder == Path('.Patcher-Temp/ORSXG5BOON3WM===')
        self.mock_decompiler.export_scripts.assert_called_once_with(
            self.swf, Path('.Patcher-Temp/ORSXG5BOON3WM===')
        )

    @patch('pathlib.Path.exists')
    def test_decompile_success_drop_cache(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.return_value = True

        folder = self.compilation_manager.decompile(self.swf, drop_cache=True)

        assert mock_path_exists.call_count == 3
        assert folder == Path('.Patcher-Temp/ORSXG5BOON3WM===')
        self.mock_decompiler.export_scripts.assert_called_once_with(
            self.swf, Path('.Patcher-Temp/ORSXG5BOON3WM===')
        )

    @patch('pathlib.Path.exists')
    def test_decompile_success_cached(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
    ) -> None:
        mock_path_exists.return_value = True

        folder = self.compilation_manager.decompile(self.swf)

        assert mock_path_exists.call_count == 3
        assert folder == Path('.Patcher-Temp/ORSXG5BOON3WM===')
        self.mock_decompiler.assert_not_called()

    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.exists')
    def test_decompile_success_create_folders(
        self: CompilationManagerSpec,
        mock_path_exists: MagicMock,
        mock_path_mkdir: MagicMock
    ) -> None:
        mock_path_exists.side_effect = [False, True, False, False]

        folder = self.compilation_manager.decompile(self.swf)

        assert mock_path_exists.call_count == 4
        assert folder == Path('.Patcher-Temp/ORSXG5BOON3WM===')
        self.mock_decompiler.export_scripts.assert_called_once_with(
            self.swf, Path('.Patcher-Temp/ORSXG5BOON3WM===')
        )

        assert mock_path_mkdir.call_count == 2

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

    def test_recompile_with_check_success(
        self: CompilationManagerSpec,
    ) -> None:
        self.mock_decompiler.recompile_data.return_value = True

        self.compilation_manager.recompile_with_check("Script", self.folder, self.swf, self.swf)

        self.mock_decompiler.recompile_data.assert_called_once_with(
            "Script", self.folder, self.swf, self.swf
        )

    def test_recompile_with_check_failure(
        self: CompilationManagerSpec,
    ) -> None:
        self.mock_decompiler.recompile_data.return_value = False

        with raises(DependencyError):
            self.compilation_manager.recompile_with_check(
                "Script", self.folder, self.swf, self.swf
            )

        self.mock_decompiler.recompile_data.assert_called_once_with(
            "Script", self.folder, self.swf, self.swf
        )

    def test_recompile_success_xml_mode(
            self: CompilationManagerSpec,
        ) -> None:
        self.compilation_manager.recompile(self.folder, self.folder, self.swf, xml_mode=True)
        self.mock_decompiler.rebuild_xml.assert_called_once_with(self.folder, self.swf)

    @patch('compile.compilation.CompilationManager.recompile_with_check')
    def test_recompile_success_full(
        self: CompilationManagerSpec,
        mock_recompile_with_check: MagicMock
    ) -> None:
        self.compilation_manager.recompile(
            self.folder, self.swf, self.swf, recompile_all=True
        )

        expected_calls = [
            call("Script", self.folder, self.swf, self.swf),
            call("Images", self.folder, self.swf, self.swf),
            call("Sounds", self.folder, self.swf, self.swf),
            call("Shapes", self.folder, self.swf, self.swf),
            call("Text", self.folder, self.swf, self.swf),
        ]

        mock_recompile_with_check.assert_has_calls(expected_calls)
        assert mock_recompile_with_check.call_count == 5

    @patch('compile.compilation.CompilationManager.recompile_with_check')
    def test_recompile_success_script_only(
        self: CompilationManagerSpec,
        mock_recompile_with_check: MagicMock,
    ) -> None:
        self.compilation_manager.recompile(self.folder, self.swf, self.swf)
        mock_recompile_with_check.assert_called_once_with(
            "Script", self.folder, self.swf, self.swf
        )
