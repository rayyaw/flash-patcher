import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from util.file_copy import clean_scripts, copy_file

@patch('pathlib.Path.unlink')
def test_clean_scripts_success(
    mock_path_unlink: MagicMock,
) -> None:
    clean_scripts(
        Path("../test/testdata/clean_scripts_dir"),
        set([
            Path("../test/testdata/clean_scripts_dir/file1.as"),
            Path("../test/testdata/clean_scripts_dir/__init__.py"),
        ])
    )

    assert mock_path_unlink.call_count == 2

@patch('shutil.copy')
@patch('pathlib.Path.unlink')
@patch('pathlib.Path.is_dir')
@patch('pathlib.Path.exists')
def test_copy_file_exists_success(
    mock_path_exists: MagicMock,
    mock_path_isdir: MagicMock,
    mock_path_unlink: MagicMock,
    mock_shutil_copy: MagicMock,
) -> None:
    mock_path_isdir.return_value = False
    mock_path_exists.return_value = True

    source = Path("../test/testdata/DoAction1.as")
    dest = Path("../test/testdata/DoAction2.as")

    copy_file(source, dest)

    mock_path_exists.assert_called_once_with()
    mock_path_isdir.assert_called_once_with()
    mock_path_unlink.assert_called_once_with(dest)
    mock_shutil_copy.assert_called_once_with(source, dest)

@patch('shutil.copytree')
@patch('shutil.rmtree')
@patch('pathlib.Path.is_dir')
@patch('pathlib.Path.exists')
def test_copy_directory_exists_success(
    mock_path_exists: MagicMock,
    mock_path_isdir: MagicMock,
    mock_shutil_rmtree: MagicMock,
    mock_shutil_copytree: MagicMock,
) -> None:
    mock_path_isdir.return_value = True
    mock_path_exists.return_value = True

    source = Path("../test/testdata/DoAction1.as")
    dest = Path("../test/testdata/DoAction2.as")

    copy_file(source, dest)

    mock_path_exists.assert_called_once_with()
    mock_path_isdir.assert_called_once_with()
    mock_shutil_rmtree.assert_called_once_with(dest)
    mock_shutil_copytree.assert_called_once_with(source, dest)

@patch('shutil.copy')
@patch('pathlib.Path.is_dir')
@patch('pathlib.Path.exists')
def test_copy_file_not_exists_success(
    mock_path_exists: MagicMock,
    mock_path_isdir: MagicMock,
    mock_shutil_copy: MagicMock,
) -> None:
    mock_path_isdir.return_value = False
    mock_path_exists.return_value = False

    source = Path("../test/testdata/DoAction1.as")
    dest = Path("../test/testdata/DoAction2.as")

    copy_file(source, dest)

    mock_path_exists.assert_called_once_with()
    mock_path_isdir.assert_called_once_with()
    mock_shutil_copy.assert_called_once_with(source, dest)

@patch('shutil.copytree')
@patch('pathlib.Path.is_dir')
@patch('pathlib.Path.exists')
def test_copy_directory_not_exists_success(
    mock_path_exists: MagicMock,
    mock_path_isdir: MagicMock,
    mock_shutil_copytree: MagicMock,
) -> None:
    mock_path_isdir.return_value = True
    mock_path_exists.return_value = False

    source = Path("../test/testdata/DoAction1.as")
    dest = Path("../test/testdata/DoAction2.as")

    copy_file(source, dest)

    mock_path_exists.assert_called_once_with()
    mock_path_isdir.assert_called_once_with()
    mock_shutil_copytree.assert_called_once_with(source, dest)
