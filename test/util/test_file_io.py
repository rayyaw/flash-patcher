from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pytest import raises

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.util.file_io import FileWritebackManager, \
    read_safe, readlines_safe, writelines_safe

EXAMPLE_FILE = "../test/testdata/DoAction1.as"

class FileWritebackManagerSpec (TestCase):
    @patch('pathlib.Path.open', create=True)
    def test_rw_safe_success(
        self: FileWritebackManagerSpec,
        mock_open: MagicMock,
    ) -> None:
        mock_file = MagicMock()

        mock_open.return_value.__enter__.return_value = mock_file

        with open(EXAMPLE_FILE, encoding="utf-8") as file:
            content_expected = file.read()
            mock_file.read.return_value = content_expected

        with patch.object(mock_file, 'writelines') as mock_writelines:
            with FileWritebackManager(
                Path(EXAMPLE_FILE),
                ErrorManager(".", 1),
            ) as content:
                assert content == content_expected

            mock_writelines.assert_called_once_with([content_expected])

    @patch('pathlib.Path.open', create=True)
    def test_rwlines_safe_success(
        self: FileWritebackManagerSpec,
        mock_open: MagicMock,
    ) -> None:
        mock_file = MagicMock()

        mock_open.return_value.__enter__.return_value = mock_file

        with open(EXAMPLE_FILE, encoding="utf-8") as file:
            content_expected = file.readlines()
            mock_file.readlines.return_value = content_expected

        with patch.object(mock_file, 'writelines') as mock_writelines:
            with FileWritebackManager(
                Path(EXAMPLE_FILE),
                ErrorManager(".", 1),
                readlines=True,
            ) as content:
                assert content == content_expected

            mock_writelines.assert_called_once_with(content_expected)

def test_read_safe_success() -> None:
    content_actual = read_safe(
        Path(EXAMPLE_FILE),
        ErrorManager(".", 1),
    )

    with open(EXAMPLE_FILE, encoding="utf-8") as file:
        content_expected = file.read()

    assert content_actual == content_expected


@patch('pathlib.Path.open', create=True)
def test_read_safe_failure_not_found(mock_open: MagicMock) -> None:
    mock_open.return_value.__enter__.side_effect = FileNotFoundError("file not found.")

    with raises(FileNotFoundError):
        read_safe(
            Path("../derppotato"),
            ErrorManager(".", 1),
        )

    mock_open.assert_called_once_with()

@patch('pathlib.Path.open', create=True)
def test_read_safe_failure_directory(mock_open: MagicMock) -> None:
    mock_open.return_value.__enter__.side_effect = IsADirectoryError("your file is invalid.")

    with raises(IsADirectoryError):
        read_safe(
            Path("../derppotato"),
            ErrorManager(".", 1),
        )

    mock_open.assert_called_once_with()

def test_readlines_safe_success() -> None:
    content_actual = readlines_safe(
        Path(EXAMPLE_FILE),
        ErrorManager(".", 1),
    )

    with open(EXAMPLE_FILE, encoding="utf-8") as file:
        content_expected = file.readlines()

    assert content_actual == content_expected

@patch('pathlib.Path.open', create=True)
def test_readlines_safe_failure_not_found(mock_open: MagicMock) -> None:
    mock_open.return_value.__enter__.side_effect = FileNotFoundError("file not found.")

    with raises(FileNotFoundError):
        readlines_safe(
            Path("../derppotato"),
            ErrorManager(".", 1),
        )

    mock_open.assert_called_once_with()

@patch('pathlib.Path.open', create=True)
def test_readlines_safe_failure_directory(mock_open: MagicMock) -> None:
    mock_open.return_value.__enter__.side_effect = IsADirectoryError("your file is invalid.")

    with raises(IsADirectoryError):
        readlines_safe(
            Path("../derppotato"),
            ErrorManager(".", 1),
        )

    mock_open.assert_called_once_with()

# Overwriting write is super annoying...
# We can't do it directly because TextIOWrapper is immutable
@patch('pathlib.Path.open', create=True)
def test_writelines_safe_success(mock_open: MagicMock) -> None:
    mock_file = MagicMock()

    mock_open.return_value.__enter__.return_value = mock_file

    with patch.object(mock_file, 'writelines') as mock_writelines:
        writelines_safe(
            Path(EXAMPLE_FILE),
            ["content"]
        )
        mock_writelines.assert_called_once_with(["content"])

    mock_open.assert_called_once_with("w")

@patch('pathlib.Path.open', create=True)
def test_writelines_safe_failure_not_found(mock_open: MagicMock) -> None:
    mock_open.return_value.__enter__.side_effect = FileNotFoundError("file not found.")

    with raises(FileNotFoundError):
        writelines_safe(
            Path("../derppotato"),
            ["content"],
        )

    mock_open.assert_called_once_with("w")

@patch('pathlib.Path.open', create=True)
def test_writelines_safe_failure_directory(mock_open: MagicMock) -> None:
    mock_open.return_value.__enter__.side_effect = IsADirectoryError("your file is invalid.")

    with raises(IsADirectoryError):
        writelines_safe(
            Path("../derppotato"),
            ["content"],
        )

    mock_open.assert_called_once_with("w")
