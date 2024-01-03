from __future__ import annotations

from pathlib import Path

from flash_patcher.antlr_source.PatchfileParser import PatchfileParser
from flash_patcher.antlr_source.PatchfileParserVisitor import PatchfileParserVisitor

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.inject.bulk_injection import BulkInjectionManager
from flash_patcher.inject.injection_location import InjectionLocation
from flash_patcher.inject.single_injection import SingleInjectionManager
from flash_patcher.util.file_io import FileWritebackManager

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

    def visitAddBlockHeader(
        self: PatchfileProcessor,
        ctx: PatchfileParser.AddBlockHeaderContext
    ) -> None:
        """Add the headers to the injector metadata"""
        full_path = self.decomp_location_with_scripts / ctx.FILENAME().getText()

        inject_location = InjectionLocation(ctx.locationToken())

        self.injector.add_injection_target(
            SingleInjectionManager(full_path, inject_location, self.patch_file_name, ctx.start.line)
        )
        self.modified_scripts.add(full_path)

    def visitAddBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.AddBlockContext
    ) -> None:
        """When we visit an add block, use an injector to manage injection"""
        for header in ctx.addBlockHeader():
            self.visitAddBlockHeader(header)

        stripped_text = ctx.addBlockText().getText()

        if stripped_text[0] == "\n":
            stripped_text = stripped_text[1:]

        self.injector.inject(stripped_text)
        self.injector.clear()

    def visitRemoveBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.RemoveBlockContext
    ) -> None:
        """Remove is processed manually as the command is less complex than add."""
        full_path = self.decomp_location_with_scripts / ctx.FILENAME().getText()

        # Open file, delete lines, and close it
        error_manager = ErrorManager(self.patch_file_name, ctx.start.line)

        with FileWritebackManager(full_path, error_manager, readlines=True) as current_file:
            line_start = InjectionLocation(ctx.locationToken(0)) \
                .resolve(current_file, False, error_manager)

            line_end = InjectionLocation(ctx.locationToken(1)) \
                .resolve(current_file, False, error_manager)

            if line_start is None or line_end is None:
                error_manager.raise_(
                    """Could not resolve line start or end.
                    You must provide a valid and in-bounds line number for remove.
                    """
                )

            # Exceptions will be thrown in InjectionLocation if this location is invalid
            for _ in range(line_start, line_end + 1):
                del current_file[line_start - 1]

        self.modified_scripts.add(full_path)

    # TODO
    def visitReplaceNthBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.ReplaceAllBlockContext
    ) -> None:
        """Replace the nth block. 
        Find its location as an InjectionLocation, 
        then remove it and perform a standard add-injection at that location.
        """
        pass

    # TODO - call replace nth code a bunch of times
    def visitReplaceAllBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.ReplaceAllBlockContext
    ) -> None:
        """Replace all blocks within the function, one at a time, from top to bottom."""
        pass

    def visitRoot(self: PatchfileProcessor, ctx: PatchfileParser.RootContext) -> set:
        """Root function. Call this when running the visitor."""
        super().visitRoot(ctx)
        return self.modified_scripts
