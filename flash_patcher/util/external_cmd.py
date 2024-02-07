"""Helper module for calling external commands."""
from os import chdir
from pathlib import Path
from subprocess import PIPE, CompletedProcess, run
import sys

def run_with_confirmation(args: list) -> CompletedProcess:
    """Run a subprocess, but prompt the user for confirmation before running."""

    # ANSI escape code for red color
    red_color_code = "\033[91m"

    # ANSI escape code to reset text color
    reset_color_code = "\033[0m"

    print(f"""{red_color_code}Warning: This patch contains executable files.{reset_color_code}
        These files run directly on your computer.
        They are not verified to be safe, and might damage your system. 
        Only run patches from sources that you trust.
        Are you sure you want to continue? [y/N]
    """, end="")

    confirmation = input()

    if confirmation.strip().lower() != "y":
        print(f"{red_color_code}Aborting.")
        sys.exit(1)

    output = run(args, check=True, stdout=PIPE)
    return output

def run_in_dir(args: list, directory: Path) -> CompletedProcess:
    """Run a command in the given directory."""
    cwd = Path.cwd()
    chdir(directory)
    output = run_with_confirmation(args)
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
