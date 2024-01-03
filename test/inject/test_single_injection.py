from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

from pytest import raises

from flash_patcher.exception.injection import InjectionError
from flash_patcher.inject.injection_location import InjectionLocation
from flash_patcher.inject.single_injection import SingleInjectionManager

# pylint: disable=wrong-import-order
from test.test_util.get_patch_context import get_add_patch_context

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

        location = InjectionLocation(get_add_patch_context(
            Path("../test/testdata/Patch1.patch"), 2,
        ))

        self.single_injection_manager = SingleInjectionManager(
            self.as_path,
            location,
            Path("test.patch"),
            1,
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
        mock_injection_location = MagicMock()

        # Configure the mock_open.return_value to have a mock for the TextIOWrapper
        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.readlines.return_value = self.file_content

        self.single_injection_manager.file_location = mock_injection_location
        mock_injection_location.resolve.return_value = 2

        with patch.object(mock_file, 'writelines') as mock_writelines:
            self.single_injection_manager.inject(["test\n", "// cmd: skip 3\n", "line2\n"], 1)

            self.file_content.insert(2, "test\n")
            self.file_content.insert(7, "line2\n")
            mock_writelines.assert_called_once_with(self.file_content)

        # .readlines() counts as a mock_open call for some reason
        assert mock_open.call_count == 2

        mock_injection_location.resolve.assert_called_once_with(
            self.file_content, True, self.single_injection_manager.error_manager
        )

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
        mock_file.readlines.return_value = self.file_content

        with patch.object(mock_file, 'writelines') as mock_writelines:
            self.single_injection_manager.inject(["test\n", "line2\n"], 1)
            self.file_content.extend(["test\n", "line2\n"])
            mock_writelines.assert_called_once_with(self.file_content)

        assert mock_open.call_count == 2

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
        mock_file.readlines.return_value = self.file_content

        with patch.object(mock_file, 'writelines') as mock_writelines:
            self.single_injection_manager.inject([], 1)
            mock_writelines.assert_called_once_with(self.file_content)

        assert mock_open.call_count == 2

    # Overwriting write is super annoying...
    # (For some reason patching writelines_safe doesn't work)
    @patch('pathlib.Path.open', create=True)
    def test_inject_no_location(
        self: SingleInjectionManagerSpec,
        mock_open: MagicMock,
    ) -> None:
        mock_injection_location = MagicMock()

        self.single_injection_manager.file_location = mock_injection_location
        mock_injection_location.resolve.return_value = None

        self.single_injection_manager.inject(["test\n"], 1)

        assert mock_open.call_count == 2

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
    