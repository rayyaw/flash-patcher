"""Helper module for calling external commands."""
from os import chdir
from pathlib import Path
from subprocess import PIPE, CompletedProcess, run
import sys

from flash_patcher.parse.scope import Scope

def ask_confirmation() -> None:
    """Prompt the user for confirmation before calling subprocess.run."""
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
        print(f"{red_color_code}Aborting.{reset_color_code}")
        sys.exit(1)

    # implicitly, else continue execution

def run_with_confirmation_in_dir(args: list, directory: Path, stdin: str = "") -> CompletedProcess:
    """Run a command in the given directory."""
    ask_confirmation()

    cwd = Path.cwd()
    chdir(directory)
    output = run(args, check=True, input=stdin, text=True, stdout=PIPE)
    chdir(cwd)

    return output


def check_output_in_dir(args: list, directory: Path, stdin: str = "") -> bytes:
    """Run a command in the given directory, and return its output.
    Prompt the user with a security warning first.
    """

    return run_with_confirmation_in_dir(args, directory, stdin).stdout

def get_modified_scripts_of_command(args: list, directory: Path, scope: Scope) -> set[Path]:
    """Run the specified command, and output a set of modified scripts."""
    process_stdin = scope.get_config()

    process_output = check_output_in_dir(
        args,
        directory,
        stdin=process_stdin,
    )

    process_output = process_output.strip()

    if process_output == "":
        return set()

    process_output = process_output.split(",")

    modified_scripts = set()

    for item in process_output:
        modified_scripts.add(directory / item)

    return modified_scripts
