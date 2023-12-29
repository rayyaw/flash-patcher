from pathlib import Path
from unittest.mock import MagicMock, patch

from pytest import raises

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.exception.injection import InjectionError
from flash_patcher.util.file_io import read_safe, readlines_safe, writelines_safe

def test_read_safe_success() -> None:
    content_actual = read_safe(
        Path("../test/testdata/DoAction1.as"),
        ErrorManager(".", 1),
    )

    with open("../test/testdata/DoAction1.as", encoding="utf-8") as file:
        content_expected = file.read()

    assert content_actual == content_expected


@patch('pathlib.Path.open', create=True)
def test_read_safe_failure_not_found(mock_open: MagicMock) -> None:
    mock_open.return_value.__enter__.side_effect = FileNotFoundError("file not found.")

    with raises(InjectionError):
        read_safe(
            Path("../derppotato"),
            ErrorManager(".", 1),
        )

    mock_open.assert_called_once_with()

@patch('pathlib.Path.open', create=True)
def test_read_safe_failure_directory(mock_open: MagicMock) -> None:
    mock_open.return_value.__enter__.side_effect = IsADirectoryError("your file is invalid.")

    with raises(InjectionError):
        read_safe(
            Path("../derppotato"),
            ErrorManager(".", 1),
        )

    mock_open.assert_called_once_with()

def test_readlines_safe_success() -> None:
    content_actual = readlines_safe(
        Path("../test/testdata/DoAction1.as"),
        ErrorManager(".", 1),
    )

    with open("../test/testdata/DoAction1.as", encoding="utf-8") as file:
        content_expected = file.readlines()

    assert content_actual == content_expected

@patch('pathlib.Path.open', create=True)
def test_readlines_safe_failure_not_found(mock_open: MagicMock) -> None:
    mock_open.return_value.__enter__.side_effect = FileNotFoundError("file not found.")

    with raises(InjectionError):
        readlines_safe(
            Path("../derppotato"),
            ErrorManager(".", 1),
        )

    mock_open.assert_called_once_with()

@patch('pathlib.Path.open', create=True)
def test_readlines_safe_failure_directory(mock_open: MagicMock) -> None:
    mock_open.return_value.__enter__.side_effect = IsADirectoryError("your file is invalid.")

    with raises(InjectionError):
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
            Path("../test/testdata/DoAction1.as"),
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
