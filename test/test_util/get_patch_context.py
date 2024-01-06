from pathlib import Path

from flash_patcher.antlr_source.PatchfileLexer import PatchfileLexer
from flash_patcher.antlr_source.PatchfileParser import PatchfileParser

from flash_patcher.parse.common import CommonParseManager

def get_add_patch_context(
    file: Path,
    offset: int,
) -> PatchfileParser.LocationTokenContext:
    root = CommonParseManager(PatchfileLexer, PatchfileParser).get_root(
        file
    ).addBlock(0)

    return root.addBlockHeader(offset).locationToken()

def get_replace_patch_context(
    file: Path,
    offset: int,
) -> PatchfileParser.LocationTokenContext:
    root = CommonParseManager(PatchfileLexer, PatchfileParser).get_root(
        file
    ).replaceNthBlock(0)

    return root.replaceNthBlockHeader(offset).locationToken()

def get_remove_patch_context(
    file: Path,
    offset: int,
) -> PatchfileParser.LocationTokenContext:
    root = CommonParseManager(PatchfileLexer, PatchfileParser).get_root(
        file
    )

    return root.removeBlock(offset)
