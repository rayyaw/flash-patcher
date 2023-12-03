from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

from pytest import raises

from flash_patcher.exception_handle.injection import InjectionError
from flash_patcher.inject.injection_location import InjectionLocation
from flash_patcher.inject.single_injection import SingleInjectionManager

class SingleInjectionManagerSpec (TestCase):

    as_path: Path
    file_content: list[str]
    mock_file: MagicMock
    single_injection_manager: SingleInjectionManager

    def __init__(
        self: SingleInjectionManagerSpec,
        methodName: str = "runTest",
    ) -> None:
        super().__init__(methodName)

        self.as_path = Path("../test/testdata/DoAction1.as")

        with open(self.as_path, encoding="utf-8") as file:
            self.file_content = file.readlines()

        self.single_injection_manager = SingleInjectionManager(
            self.as_path,
            InjectionLocation("end"),
            Path("test.patch"),
            1
        )

        self.mock_file = MagicMock()

    # Overwriting write is super annoying...
    # (For some reason patching writelines_safe doesn't work)
    @patch('pathlib.Path.open', create=True)
    def test_inject_success_with_command(
        self: SingleInjectionManagerSpec,
        mock_open: MagicMock,
    ) -> None:

        mock_file = MagicMock()

        # Configure the mock_open.return_value to have a mock for the TextIOWrapper
        mock_open.return_value.__enter__.return_value = mock_file
        with patch.object(mock_file, 'writelines') as mock_writelines:
            self.single_injection_manager.file_location = InjectionLocation("3")
            self.single_injection_manager.inject(["test\n", "// cmd: skip 3\n", "line2\n"], 1)

            self.file_content.insert(2, "test\n")
            self.file_content.insert(7, "line2\n")
            mock_writelines.assert_called_once_with(self.file_content)

        mock_open.assert_called_once()

    # Overwriting write is super annoying...
    # (For some reason patching writelines_safe doesn't work)
    @patch('pathlib.Path.open', create=True)
    def test_inject_success_no_command(
        self: SingleInjectionManagerSpec,
        mock_open: MagicMock,
    ) -> None:

        mock_file = MagicMock()

        # Configure the mock_open.return_value to have a mock for the TextIOWrapper
        mock_open.return_value.__enter__.return_value = mock_file
        with patch.object(mock_file, 'writelines') as mock_writelines:
            self.single_injection_manager.inject(["test\n", "line2\n"], 1)
            self.file_content.extend(["test\n", "line2\n"])
            mock_writelines.assert_called_once_with(self.file_content)

        mock_open.assert_called_once()

    # Overwriting write is super annoying...
    # (For some reason patching writelines_safe doesn't work)
    @patch('pathlib.Path.open', create=True)
    def test_inject_success_empty(
        self: SingleInjectionManagerSpec,
        mock_open: MagicMock,
    ) -> None:

        mock_file = MagicMock()

        # Configure the mock_open.return_value to have a mock for the TextIOWrapper
        mock_open.return_value.__enter__.return_value = mock_file
        with patch.object(mock_file, 'writelines') as mock_writelines:
            self.single_injection_manager.inject([], 1)
            mock_writelines.assert_called_once_with(self.file_content)

        mock_open.assert_called_once()

    def test_inject_failure_invalid_command(
        self: SingleInjectionManagerSpec,
    ) -> None:
        with raises(InjectionError):
            self.single_injection_manager.inject(["test\n", "// cmd: invalid\n"], 1)

    def test_handle_secondary_command_success_skip_command(
        self: SingleInjectionManagerSpec,
    ) -> None:
        new_line_no, was_command = self.single_injection_manager.handle_secondary_command(
            1, "// cmd: skip 10"
        )

        assert was_command
        assert new_line_no == 11

    def test_handle_secondary_command_success_not_command(
        self: SingleInjectionManagerSpec,
    ) -> None:
        new_line_no, was_command = self.single_injection_manager.handle_secondary_command(
            1, "// not a skip command"
        )

        assert not was_command
        assert new_line_no == 1

    def test_handle_secondary_command_failure_invalid_command(
        self: SingleInjectionManagerSpec,
    ) -> None:
        with raises(InjectionError):
            self.single_injection_manager.handle_secondary_command(
                1, "// cmd: aeiou"
            )

    def test_handle_secondary_skip_command_success(
        self: SingleInjectionManagerSpec
    ) -> None:
        new_line_no = self.single_injection_manager.handle_secondary_skip_command(
            1, "// cmd: skip 15"
        )

        assert new_line_no == 16

    def test_handle_secondary_skip_command_failure_invalid_amount_str(
        self: SingleInjectionManagerSpec
    ) -> None:
        with raises(InjectionError):
            self.single_injection_manager.handle_secondary_skip_command(
                1, "// cmd: skip aeiou"
            )

    def test_handle_secondary_skip_command_failure_invalid_amount_float(
        self: SingleInjectionManagerSpec
    ) -> None:
        with raises(InjectionError):
            self.single_injection_manager.handle_secondary_skip_command(
                1, "// cmd: skip 3.2"
            )
    