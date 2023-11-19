import os
import shutil
from pathlib import Path

def clean_scripts(decomp_location: Path, modified_scripts: set[Path]) -> None:
    """Delete all non-modified scripts.

    Taken from https://stackoverflow.com/questions/19309667/recursive-os-listdir
    - Make recursive os.listdir.
    """
    scripts = [
        Path(dp, f) for dp, _, fn in os.walk(decomp_location.expanduser()) for f in fn
    ]

    for script in scripts:
        if script not in modified_scripts:
            script.unlink()

def copy_file(source: Path, dest: Path) -> None:
    """Copy a file or folder."""
    isdir = source.is_dir()
    if dest.exists():
        if isdir:
            shutil.rmtree(dest)
        else:
            Path.unlink(dest)

    if isdir:
        shutil.copytree(source, dest)
    else:
        shutil.copy(source, dest)
