"""Helper module for calling external commands."""
from os import chdir
from pathlib import Path
from subprocess import PIPE, CompletedProcess, run

def run_in_dir(args: list, directory: Path) -> CompletedProcess:
    """Run a command in the given directory."""
    cwd = Path.cwd()
    chdir(directory)
    output = run(args, check=True, stdout=PIPE)
    chdir(cwd)

    return output


def check_output_in_dir(args: list, directory: Path) -> bytes:
    """Run a command in the given directory, and return its output."""
    return run_in_dir(args, directory).stdout

def get_modified_scripts_of_command(args: list, directory: Path) -> set[Path]:
    """Run the specified command, and output a set of modified scripts."""
    process_output = check_output_in_dir(
        args,
        directory,
    )
    process_output = process_output.decode('utf-8').strip()

    if process_output == "":
        return set()

    process_output = process_output.split(",")

    modified_scripts = set()

    for item in process_output:
        modified_scripts.add(directory / item)

    return modified_scripts
