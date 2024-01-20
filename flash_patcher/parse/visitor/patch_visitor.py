from __future__ import annotations

from pathlib import Path

from flash_patcher.antlr_source.PatchfileParser import PatchfileParser
from flash_patcher.antlr_source.PatchfileParserVisitor import PatchfileParserVisitor

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.inject.bulk_injection import BulkInjectionManager
from flash_patcher.inject.location.parser_injection_location import ParserInjectionLocation
from flash_patcher.inject.find_content import FindContentManager
from flash_patcher.inject.single_injection import SingleInjectionManager
from flash_patcher.util.file_io import FileWritebackManager, read_safe, writelines_safe

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

        inject_location = ParserInjectionLocation(ctx.locationToken())

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
            line_start = ParserInjectionLocation(ctx.locationToken(0)) \
                .resolve(current_file, False, error_manager)

            line_end = ParserInjectionLocation(ctx.locationToken(1)) \
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

    def visitReplaceNthBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.ReplaceNthBlockContext
    ) -> None:
        """Replace the nth block. 
        Find its location as an InjectionLocation, 
        then remove it and perform a standard add-injection at that location.
        """
        for i in ctx.replaceNthBlockHeader():
            full_path = self.decomp_location_with_scripts / i.FILENAME().getText()
            error_manager = ErrorManager(self.patch_file_name, i.start.line)

            current_file = read_safe(full_path, error_manager)
            updated_file, replace_location = FindContentManager(
                i.locationToken(), ctx.replaceBlockText().getText().strip()
            ).resolve(current_file, error_manager)

            injector = SingleInjectionManager(
                full_path, replace_location, full_path, i.start.line
            )

            injector.file_content = updated_file
            injector.inject(ctx.addBlockText().getText().strip(), i.start.line)

            self.modified_scripts.add(full_path)

    def visitReplaceAllBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.ReplaceAllBlockContext
    ) -> None:
        """Replace all instances of the specified content.
        Does not support secondary commands, only direct text replacement.
        """
        find_content = ctx.replaceBlockText().getText().strip()
        replace_content = ctx.addBlockText().getText().strip()

        for i in ctx.replaceAllBlockHeader():

            full_path = self.decomp_location_with_scripts / i.FILENAME().getText()
            error_manager = ErrorManager(self.patch_file_name, i.start.line)

            content = read_safe(full_path, error_manager)
            content = content.replace(find_content, replace_content)
            writelines_safe(full_path, [content])

            self.modified_scripts.add(full_path)

    def visitRoot(self: PatchfileProcessor, ctx: PatchfileParser.RootContext) -> set:
        """Root function. Call this when running the visitor."""
        super().visitRoot(ctx)
        return self.modified_scripts
