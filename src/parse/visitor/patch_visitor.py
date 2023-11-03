from __future__ import annotations

import sys
from antlr_source.PatchfileParser import PatchfileParser
from antlr_source.PatchfileParserVisitor import PatchfileParserVisitor
from logging import exception
from pathlib import Path

from inject.bulk_injection import BulkInjectionManager
from inject.injection_location import InjectionLocation
from inject.single_injection import SingleInjectionManager
from util.exception import ErrorManager
from util.file_io import read_from_file, write_to_file

class PatchfileProcessor (PatchfileParserVisitor):

    injector: BulkInjectionManager
    modifiedScripts: set
    patchFileName: Path
    decompLocationWithScripts: Path

    def __init__(
        self: PatchfileProcessor,
        patch_file_name: Path,
        decomp_location_with_scripts: Path
    ) -> None:
        self.patchFileName = patch_file_name
        self.decompLocationWithScripts = decomp_location_with_scripts

        self.injector = BulkInjectionManager()
        self.modifiedScripts = set()
    
    def visitAddBlockHeader(self, ctx: PatchfileParser.AddBlockHeaderContext):
        full_path = self.decompLocationWithScripts / ctx.FILENAME().getText()

        inject_location = InjectionLocation(ctx.FILE_ADD_TOKEN().getText())

        self.injector.add_injection_target(
            SingleInjectionManager(full_path, inject_location, self.patchFileName, ctx.start.line)
        )
        self.modifiedScripts.add(full_path)

    def visitAddBlock(self, ctx: PatchfileParser.AddBlockContext) -> None:
        for header in ctx.addBlockHeader():
            self.visitAddBlockHeader(header)

        self.injector.injectContent(ctx.addBlockText().getText())

    def visitRemoveBlock(self, ctx: PatchfileParser.RemoveBlockContext) -> None:
        full_path = self.decompLocationWithScripts / ctx.FILENAME().getText()

        line_start, line_end = ctx.NUMBER_RANGE().getText().split("-")
        line_start = int(line_start)
        line_end = int(line_end)

        # Open file, delete lines, and close it
        error_manager = ErrorManager(self.patchFileName, ctx.start.line)
        current_file = read_from_file(full_path, error_manager)

        try:
            for _ in range(line_start, line_end + 1):
                del current_file[line_start - 1]
        except IndexError:
            exception(
                """%s, line %d: Out of range.
                Line number %d out of range for file %s.
                Aborting...""",
                self.patchFileName,
                ctx.start.line,
                line_end,
                full_path.as_posix(),
            )
            sys.exit(1)

        write_to_file(full_path, current_file)

        self.modifiedScripts.add(full_path)

    def visitRoot(self, ctx: PatchfileParser.RootContext) -> set:
        super().visitRoot(ctx)
        return self.modifiedScripts