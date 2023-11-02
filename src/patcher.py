from __future__ import annotations

import os
import shutil
import sys
from logging import basicConfig, exception, info
from pathlib import Path

from compile.compilation import CompilationManager
from parse.asset import AssetFileParser
from parse.patch import PatchFileParser

"""
Riley's SWF patcher - a tool to patch content into SWF files.

Development: RileyTech, qtkito, GTcreyon
Windows path fix: Jhynjhiruu

Download and updates: https://github.com/rayyaw/flash-patcher

License: CC-BY SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0)

Dependencies: Python 3, JPEXS Decompiler (https://github.com/jindrapetrik/jpexs-decompiler/releases)

Inject arbitrary code, images, and more into existing SWFs!
See the README for documentation and license.
"""

basicConfig(level=1, format="%(levelname)s: %(message)s")

CURRENT_VERSION = "v4.1.8"

DECOMP_LOCATION = Path("./.Patcher-Temp/mod/")
DECOMP_LOCATION_WITH_SCRIPTS = Path(DECOMP_LOCATION, "scripts/")

def clean_scripts(modified_scripts: set) -> None:
    """Delete all non-modified scripts.

    Taken from https://stackoverflow.com/questions/19309667/recursive-os-listdir
    - Make recursive os.listdir.
    """
    scripts = [
        Path(dp, f) for dp, _, fn in os.walk(DECOMP_LOCATION.expanduser()) for f in fn
    ]
    
    for script in scripts:
        if script not in modified_scripts:
            script.unlink()

def apply_patches(patches: list, folder: Path) -> set:
    """Apply every patch, ignoring comments and empty lines."""
    modified_scripts = set()
    for patch in patches:
        patch_stripped = patch.strip("\n\r ")
        if len(patch_stripped) == 0 or patch_stripped[0] == "#":
            continue

        # Check file extension of file
        if patch_stripped.endswith(".patch"):  # Patch (code) file
            modified_scripts |= \
                PatchFileParser(folder / patch_stripped, DECOMP_LOCATION_WITH_SCRIPTS).parse()
        elif patch_stripped.endswith(".assets"):  # Asset Pack file
            modified_scripts |= \
                AssetFileParser(folder / patch_stripped, folder, DECOMP_LOCATION).parse()
        else:
            exception(
                """The file provided ('%s') did not have a valid filetype.
                Aborting...""",
                patch_stripped,
            )
            sys.exit(1)

    return modified_scripts

def main(
    inputfile: Path,
    folder: Path,
    stagefile: Path,
    output: Path,
    drop_cache: bool,
    recompile_all: bool,
    xml_mode: bool,
) -> None:
    """Run the patcher."""
    info("Riley's SWF Patcher - %s", CURRENT_VERSION)

    try:
        compiler = CompilationManager()
    except ModuleNotFoundError:
        exception(
            "Could not locate required dependency: JPEXS Flash Decompiler. Aborting...",
        )
        sys.exit(1)

    if xml_mode:
        info("XML decompilation mode.")
        global DECOMP_LOCATION
        global DECOMP_LOCATION_WITH_SCRIPTS

        DECOMP_LOCATION = Path("./.Patcher-Temp/swf.xml")
        DECOMP_LOCATION_WITH_SCRIPTS = Path("./.Patcher-Temp/")

    cache_location = compiler.decompile(
        inputfile,
        drop_cache=drop_cache,
        xml_mode=xml_mode,
    )

    # Copy the cache to a different location so we can reuse it
    isdir = cache_location.is_dir()
    if DECOMP_LOCATION.exists():
        if isdir:
            shutil.rmtree(DECOMP_LOCATION)
        else:
            Path.unlink(DECOMP_LOCATION)

    if isdir:
        shutil.copytree(cache_location, DECOMP_LOCATION)
    else:
        shutil.copy(cache_location, DECOMP_LOCATION)

    info("Decompilation finished. Beginning injection...")

    try:
        # Open the stage file and read list of all patches to apply
        with Path.open(folder / stagefile) as f:
            patches_to_apply = f.readlines()
    except FileNotFoundError:
        exception(
            """Could not open stage file: %s.
            Aborting...""",
            Path(folder / stagefile),
        )
        sys.exit(1)

    modified_scripts = apply_patches(patches_to_apply, folder)

    info("Injection complete, cleaning up...")

    clean_scripts(modified_scripts)

    info("Recompiling...")

    compiler.recompile(
        DECOMP_LOCATION,
        inputfile,
        output,
        recompile_all=recompile_all,
        xml_mode=xml_mode,
    )

    info("Done.")
