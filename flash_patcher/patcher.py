from importlib.metadata import PackageNotFoundError, version
# pylint: disable=no-name-in-module
from logging import DEBUG
from pathlib import Path

from flash_patcher.compile.compilation import CompilationManager
from flash_patcher.compile.locate_decomp import get_decomp_locations
from flash_patcher.exception.dependency import DependencyError
from flash_patcher.parse.patch import PatchfileManager
from flash_patcher.util.file_copy import clean_scripts, copy_file
from flash_patcher.util.logging import logger

# pylint: disable=pointless-string-statement
"""
rayyaw's SWF patcher - a tool to patch content into SWF files.

Development: rayyaw, qtkito, GTcreyon
Windows path fix: Jhynjhiruu

Download and updates: https://github.com/rayyaw/flash-patcher

License: CC-BY SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0)

Dependencies: Python 3, JPEXS Decompiler (https://github.com/jindrapetrik/jpexs-decompiler/releases)

Inject arbitrary code, images, and more into existing SWFs!
See the README for documentation and license.
"""

def print_version() -> None:
    """Print the Flash Patcher version."""
    try:
        __version__ = version("flash_patcher")
    except PackageNotFoundError:
        __version__ = "Unit Tests"

    logger.info("rayyaw's SWF Patcher - v%s", __version__)

def main(
    inputfile: Path,
    folder: Path,
    mainfile: Path,
    output: Path,
    drop_cache: bool = False,
    recompile_all: bool = False,
    xml_mode: bool = False,
    verbose: bool = False,
) -> None:
    """Run the patcher."""
    if verbose:
        logger.setLevel(DEBUG)

    print_version()

    try:
        compiler = CompilationManager()
    except ModuleNotFoundError as exc:
        error_mesg = "Could not locate required dependency: JPEXS Flash Decompiler. Aborting..."
        logger.exception(error_mesg)
        raise DependencyError(error_mesg) from exc

    decomp_location, decomp_location_with_scripts = get_decomp_locations(xml_mode)

    cache_location = compiler.decompile(
        inputfile,
        drop_cache=drop_cache,
        xml_mode=xml_mode,
    )

    # Copy the cache to a different location so we can reuse it
    copy_file(cache_location, decomp_location)

    logger.info("Decompilation finished. Beginning injection...")

    modified_scripts = PatchfileManager(
        decomp_location,
        decomp_location_with_scripts,
        folder / mainfile,
        folder,
    ).parse()

    logger.info("Injection complete, cleaning up...")

    clean_scripts(decomp_location, modified_scripts)

    logger.info("Recompiling...")

    compiler.recompile(
        decomp_location,
        inputfile,
        output,
        recompile_all=recompile_all,
        xml_mode=xml_mode,
    )

    logger.info("Done.")
