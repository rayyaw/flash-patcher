from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import MagicMock, patch

from pytest import raises

from flash_patcher.parse.scope import Scope
from flash_patcher.util.external_cmd import \
    ask_confirmation, run_with_confirmation_in_dir, check_output_in_dir, \
    get_modified_scripts_of_command

@patch("sys.exit")
@patch("builtins.input")
def test_run_with_confirmation_success(
    mock_input: MagicMock,
    mock_exit: MagicMock,
) -> None:
    mock_input.return_value = "y"
    ask_confirmation()

    mock_exit.assert_not_called()

@patch("sys.exit")
@patch("builtins.input")
def test_run_with_confirmation_exit(
    mock_input: MagicMock,
    mock_exit: MagicMock
) -> None:
    mock_input.return_value = "n"
    ask_confirmation()

    mock_exit.assert_called_once_with(1)

@patch("builtins.input")
def test_run_in_dir_success(mock_input: MagicMock) -> None:
    mock_input.return_value = "y"
    output = run_with_confirmation_in_dir(
        ["python",  "../test/testdata/python/ls_main.py"],
        Path("flash_patcher")
    )

    assert output.returncode == 0
    assert output.stdout == "__main__.py\n"

@patch("builtins.input")
def test_run_in_dir_failure(mock_input: MagicMock) -> None:
    mock_input.return_value = "y"

    with raises(CalledProcessError):
        run_with_confirmation_in_dir(
            ["python", "testdata/python/exception.py"],
            Path("test/")
        )

@patch("builtins.input")
def test_check_output_in_dir_success(mock_input: MagicMock) -> None:
    mock_input.return_value = "y"

    output = check_output_in_dir(
        ["python",  "../test/testdata/python/ls_main.py"],
        Path("flash_patcher")
    )

    assert output == "__main__.py\n"

@patch("builtins.input")
def test_get_modified_scripts_of_command_success(mock_input: MagicMock) -> None:
    mock_input.return_value = "y"

    output = get_modified_scripts_of_command(
        ["python3", "testdata/python/sample.py"],
        Path("test/"),
        Scope(),
    )

    assert output == set([
        Path("test/DoAction1.as"),
        Path("test/DoAction2.as"),
    ])

@patch("builtins.input")
def test_get_modified_scripts_of_command_with_scope(mock_input: MagicMock) -> None:
    mock_input.return_value = "y"

    scope = Scope()
    scope.define_local("key1", "val1")
    scope.define_local("key2", "val2")

    output = get_modified_scripts_of_command(
        ["python3", "testdata/python/assert.py"],
        Path("test/"),
        scope,
    )

    assert output == set()

@patch("builtins.input")
def test_get_modified_scripts_of_command_empty(mock_input: MagicMock) -> None:
    mock_input.return_value = "y"

    output = get_modified_scripts_of_command(
        ["python3", "testdata/python/empty.py"],
        Path("test/"),
        Scope(),
    )

    assert output == set()
