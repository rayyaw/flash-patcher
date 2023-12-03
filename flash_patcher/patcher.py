from logging import basicConfig, exception, info
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from flash_patcher.compile.compilation import CompilationManager
from flash_patcher.compile.locate_decomp import get_decomp_locations
from flash_patcher.exception_handle.dependency import DependencyError
from flash_patcher.parse.stage import StagefileManager
from flash_patcher.util.file_copy import clean_scripts, copy_file

# pylint: disable=pointless-string-statement
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

def main(
    inputfile: Path,
    folder: Path,
    stagefile: Path,
    output: Path,
    drop_cache: bool = False,
    recompile_all: bool = False,
    xml_mode: bool = False,
) -> None:
    """Run the patcher."""
    try:
        __version__ = version("flash_patcher")
    except PackageNotFoundError:
        __version__ = "Unit Tests"

    info(f"Riley's SWF Patcher - v{__version__}")

    try:
        compiler = CompilationManager()
    except ModuleNotFoundError as exc:
        error_mesg = "Could not locate required dependency: JPEXS Flash Decompiler. Aborting..."
        exception(error_mesg)
        raise DependencyError(error_mesg) from exc

    decomp_location, decomp_location_with_scripts = get_decomp_locations(xml_mode)

    cache_location = compiler.decompile(
        inputfile,
        drop_cache=drop_cache,
        xml_mode=xml_mode,
    )

    # Copy the cache to a different location so we can reuse it
    copy_file(cache_location, decomp_location)

    info("Decompilation finished. Beginning injection...")

    modified_scripts = StagefileManager(
        folder,
        stagefile,
        decomp_location,
        decomp_location_with_scripts
    ).parse()

    info("Injection complete, cleaning up...")

    clean_scripts(decomp_location, modified_scripts)

    info("Recompiling...")

    compiler.recompile(
        decomp_location,
        inputfile,
        output,
        recompile_all=recompile_all,
        xml_mode=xml_mode,
    )

    info("Done.")
