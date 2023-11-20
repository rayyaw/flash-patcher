from __future__ import annotations

import sys
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from compile.jpexs import JPEXSInterface

class JPEXSInterfaceSpec (TestCase):

    interface:               JPEXSInterface
    subprocess_mock_success: MagicMock
    subprocess_mock_failure: MagicMock

    def __init__(self: JPEXSInterfaceSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        # Manual initialization required for the default test case
        self.interface = JPEXSInterface("/usr/bin/ffdec", ["--derppotato"])

        self.subprocess_mock_success = MagicMock(returncode=0, stdout='', stderr='')
        self.subprocess_mock_failure = MagicMock(returncode=1, stdout='', stderr='Error!')

    def test_sanity(self: JPEXSInterfaceSpec) -> None:
        assert True

    # JPEXS installation tests
    @patch('pathlib.Path.exists')
    def test_automatic_installation_apt_success(
        self: JPEXSInterfaceSpec,
        mock_path_exists: MagicMock
    ) -> None:

        mock_path_exists.return_value = True
        success = self.interface.install_jpexs(Path("/usr/bin/ffdec"))

        mock_path_exists.assert_called_once_with()
        assert self.interface.path == Path("/usr/bin/ffdec")
        assert self.interface.args == []
        assert success

    @patch('pathlib.Path.exists')
    def test_automatic_installation_apt_failure(
        self: JPEXSInterfaceSpec,
        mock_path_exists: MagicMock
    ) -> None:

        mock_path_exists.return_value = False
        success = self.interface.install_jpexs(Path("/usr/bin/ffdec"))

        assert mock_path_exists.call_count == 2
        assert not success

    @patch('pathlib.Path.exists')
    @patch('subprocess.run')
    # For whatever reason, the order of mocks is passed in reverse
    def test_automatic_installation_flatpak_success(
        self: JPEXSInterfaceSpec,
        mock_subprocess_run: MagicMock,
        mock_path_exists: MagicMock,
    ) -> None:

        mock_path_exists.return_value = True
        mock_subprocess_run.return_value = self.subprocess_mock_success

        success = self.interface.install_jpexs(Path("/usr/bin/flatpak"), ["run", "--branch=stable"])

        assert mock_path_exists.call_count == 2
        assert self.interface.path == Path("/usr/bin/flatpak")
        assert self.interface.args == ["run", "--branch=stable"]

        assert success

    @patch('pathlib.Path.exists')
    @patch('subprocess.run')
    def test_automatic_installation_flatpak_failure(
        self: JPEXSInterfaceSpec,
        mock_subprocess_run: MagicMock,
        mock_path_exists: MagicMock,
    ) -> None:

        mock_path_exists.return_value = True
        mock_subprocess_run.return_value = self.subprocess_mock_failure

        success = self.interface.install_jpexs(Path("/usr/bin/flatpak"), ["run", "--branch=stable"])

        assert mock_path_exists.call_count == 2
        assert not success

    # JPEXS calling tests
    @patch('subprocess.run')
    def test_dump_xml_success(self: JPEXSInterfaceSpec, mock_subprocess_run: MagicMock) -> None:
        input_swf = Path("./.Patcher-Temp/base.swf")
        output = Path("./folder")

        mock_subprocess_run.return_value = self.subprocess_mock_success

        success = self.interface.dump_xml(input_swf, output)

        mock_subprocess_run.assert_called_once_with([
            '/usr/bin/ffdec',
            '--derppotato',
            '-swf2xml',
            input_swf,
            output,
        ], stdout=-3, stderr=-3, check=False)
        assert success

    @patch('subprocess.run')
    def test_dump_xml_failure(self: JPEXSInterfaceSpec, mock_subprocess_run: MagicMock) -> None:
        input_swf = Path("./.Patcher-Temp/base.swf")
        output = Path("./folder")

        mock_subprocess_run.return_value = self.subprocess_mock_failure

        success = self.interface.dump_xml(input_swf, output)

        mock_subprocess_run.assert_called_once_with([
            '/usr/bin/ffdec',
            '--derppotato',
            '-swf2xml',
            input_swf,
            output,
        ], stdout=-3, stderr=-3, check=False)
        assert not success

    @patch('subprocess.run')
    def test_rebuild_xml_success(self: JPEXSInterfaceSpec, mock_subprocess_run: MagicMock) -> None:
        input_folder = Path("./.Patcher-Temp/base")
        output = Path("./folder/file.swf")

        mock_subprocess_run.return_value = self.subprocess_mock_success

        success = self.interface.rebuild_xml(input_folder, output)

        mock_subprocess_run.assert_called_once_with([
            '/usr/bin/ffdec',
            '--derppotato',
            '-xml2swf',
            input_folder,
            output,
        ], stdout=-3, check=False)
        assert success

    @patch('subprocess.run')
    def test_rebuild_xml_failure(self: JPEXSInterfaceSpec, mock_subprocess_run: MagicMock) -> None:
        input_folder = Path("./.Patcher-Temp/base")
        output = Path("./folder/file.swf")

        mock_subprocess_run.return_value = self.subprocess_mock_failure

        success = self.interface.rebuild_xml(input_folder, output)

        mock_subprocess_run.assert_called_once_with([
            '/usr/bin/ffdec',
            '--derppotato',
            '-xml2swf',
            input_folder,
            output,
        ], stdout=-3, check=False)
        assert not success

    @patch('subprocess.run')
    def test_export_scripts_success(
        self: JPEXSInterfaceSpec,
        mock_subprocess_run: MagicMock
    ) -> None:
        input_file = Path("base.swf")
        output = Path("./folder")

        mock_subprocess_run.return_value = self.subprocess_mock_success

        success = self.interface.export_scripts(input_file, output)

        mock_subprocess_run.assert_called_once_with([
            '/usr/bin/ffdec',
            '--derppotato',
            '-config',
            'autoDeobfuscate=1,parallelSpeedUp=0',
            '-export',
            'script',
            output,
            input_file,
        ], stdout=-3, stderr=-3, check=False)
        assert success

    @patch('subprocess.run')
    def test_export_scripts_failure(
        self: JPEXSInterfaceSpec,
        mock_subprocess_run: MagicMock
    ) -> None:
        input_file = Path("base.swf")
        output = Path("./folder")

        mock_subprocess_run.return_value = self.subprocess_mock_failure

        success = self.interface.export_scripts(input_file, output)

        mock_subprocess_run.assert_called_once_with([
            '/usr/bin/ffdec',
            '--derppotato',
            '-config',
            'autoDeobfuscate=1,parallelSpeedUp=0',
            '-export',
            'script',
            output,
            input_file,
        ], stdout=-3, stderr=-3, check=False)
        assert not success

    @patch('subprocess.run')
    def test_recompile_data_success(
        self: JPEXSInterfaceSpec,
        mock_subprocess_run: MagicMock
    ) -> None:
        input_folder = Path("./.Patcher-Temp/mod")
        swf = Path("test.swf")
        output = Path("./folder")

        mock_subprocess_run.return_value = self.subprocess_mock_success

        success = self.interface.recompile_data("Script", input_folder, swf, output)

        mock_subprocess_run.assert_called_once_with([
            '/usr/bin/ffdec',
            '--derppotato',
            '-importScript',
            swf,
            output,
            input_folder,
        ], stdout=-3, check=False)
        assert success

    @patch('subprocess.run')
    def test_recompile_data_failure(
        self: JPEXSInterfaceSpec,
        mock_subprocess_run: MagicMock
    ) -> None:
        input_folder = Path("./.Patcher-Temp/mod")
        swf = Path("test.swf")
        output = Path("./folder")

        mock_subprocess_run.return_value = self.subprocess_mock_failure

        success = self.interface.recompile_data("Script", input_folder, swf, output)

        mock_subprocess_run.assert_called_once_with([
            '/usr/bin/ffdec',
            '--derppotato',
            '-importScript',
            swf,
            output,
            input_folder,
        ], stdout=-3, check=False)
        assert not success
