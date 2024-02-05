from pathlib import Path
from subprocess import CalledProcessError

from pytest import raises

from flash_patcher.util.external_cmd import \
    run_in_dir, check_output_in_dir, get_modified_scripts_of_command

def test_run_in_dir_success() -> None:
    output = run_in_dir(
        ["ls",  "README.md"],
        Path("../")
    )

    assert output.returncode == 0
    assert output.stdout == b"README.md\n"

def test_run_in_dir_failure() -> None:
    with raises(CalledProcessError):
        run_in_dir(
            # ls [nonexistent file] will return a nonzero exit code
            ["ls", "README.md"],
            Path("../test/")
        )

def test_check_output_in_dir_success() -> None:
    output = check_output_in_dir(
        ["ls",  "README.md"],
        Path("../")
    )

    assert output == b"README.md\n"

def test_get_modified_scripts_of_command_success() -> None:
    output = get_modified_scripts_of_command(
        ["echo", "a,b,c"],
        Path("../")
    )

    assert output == set([
        Path("../a"),
        Path("../b"),
        Path("../c"),
    ])

def test_get_modified_scripts_of_command_empty() -> None:
    output = get_modified_scripts_of_command(
        ["echo"],
        Path("../")
    )

    assert output == set()
