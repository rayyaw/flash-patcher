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
