from __future__ import annotations

from logging import exception
from pathlib import Path

from flash_patcher.antlr_source.PatchfileParser import PatchfileParser
from flash_patcher.antlr_source.PatchfileParserVisitor import PatchfileParserVisitor

from flash_patcher.exception_handle.error_manager import ErrorManager
from flash_patcher.inject.bulk_injection import BulkInjectionManager
from flash_patcher.inject.injection_location import InjectionLocation
from flash_patcher.inject.single_injection import SingleInjectionManager
from flash_patcher.util.file_io import readlines_safe, writelines_safe

class PatchfileProcessor (PatchfileParserVisitor):
    """This class inherits from the ANTLR visitor to process patch files.
    
    It will automatically take in the file syntax tree and perform the injections in it. 
    """

    injector: BulkInjectionManager
    modified_scripts: set[Path]
    patch_file_name: Path
    decomp_location_with_scripts: Path

    def __init__(
        self: PatchfileProcessor,
        patch_file_name: Path,
        decomp_location_with_scripts: Path
    ) -> None:
        self.patch_file_name = patch_file_name
        self.decomp_location_with_scripts = decomp_location_with_scripts

        self.injector = BulkInjectionManager()
        self.modified_scripts = set()

    def visitAddBlockHeader(self, ctx: PatchfileParser.AddBlockHeaderContext) -> None:
        """Add the headers to the injector metadata"""
        full_path = self.decomp_location_with_scripts / ctx.FILENAME().getText()

        inject_location = InjectionLocation(ctx.FILE_ADD_TOKEN().getText())

        self.injector.add_injection_target(
            SingleInjectionManager(full_path, inject_location, self.patch_file_name, ctx.start.line)
        )
        self.modified_scripts.add(full_path)

    def visitAddBlock(self, ctx: PatchfileParser.AddBlockContext) -> None:
        """When we visit an add block, use an injector to manage injection"""
        for header in ctx.addBlockHeader():
            self.visitAddBlockHeader(header)

        stripped_text = ctx.addBlockText().getText()

        if stripped_text[0] == "\n":
            stripped_text = stripped_text[1:]

        self.injector.inject(stripped_text)
        self.injector.clear()

    def visitRemoveBlock(self, ctx: PatchfileParser.RemoveBlockContext) -> None:
        """Remove is processed manually as the command is less complex than add."""
        full_path = self.decomp_location_with_scripts / ctx.FILENAME().getText()

        line_start, line_end = ctx.NUMBER_RANGE().getText().split("-")
        line_start = int(line_start)
        line_end = int(line_end)

        # Open file, delete lines, and close it
        error_manager = ErrorManager(self.patch_file_name, ctx.start.line)
        current_file = readlines_safe(full_path, error_manager)

        try:
            for _ in range(line_start, line_end + 1):
                del current_file[line_start - 1]
        except IndexError as exc:
            exception(
                """%s, line %d: Out of range.
                Line number %d out of range for file %s.
                Aborting...""",
                self.patch_file_name,
                ctx.start.line,
                line_end,
                full_path.as_posix(),
            )
            raise exc

        writelines_safe(full_path, current_file)

        self.modified_scripts.add(full_path)

    def visitRoot(self, ctx: PatchfileParser.RootContext) -> set:
        """Root function. Call this when running the visitor."""
        super().visitRoot(ctx)
        return self.modified_scripts
