from __future__ import annotations

import shutil
from pathlib import Path

from flash_patcher.antlr_source.PatchfileParser import PatchfileParser
from flash_patcher.antlr_source.PatchfileParserVisitor import PatchfileParserVisitor

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.inject.bulk_injection import BulkInjectionManager
from flash_patcher.inject.location.parser_injection_location import ParserInjectionLocation
from flash_patcher.inject.find_content import FindContentManager
from flash_patcher.inject.single_injection import SingleInjectionManager
from flash_patcher.parse.scope import Scope
from flash_patcher.util.external_cmd import get_modified_scripts_of_command
from flash_patcher.util.file_io import FileWritebackManager, read_safe, writelines_safe
from flash_patcher.util.logging import logger

class PatchfileProcessor (PatchfileParserVisitor):
    """This class inherits from the ANTLR visitor to process patch files.
    
    It will automatically take in the file syntax tree and perform the injections in it. 
    """

    injector: BulkInjectionManager
    modified_scripts: set[Path]
    patch_file_name: Path
    scope: Scope

    folder: Path
    decomp_location: Path
    decomp_location_with_scripts: Path

    def __init__(
        self: PatchfileProcessor,
        patch_file_name: Path,
        folder: Path,
        decomp_location: Path,
        decomp_location_with_scripts: Path,
        scope: Scope = None,
    ) -> None:
        self.patch_file_name = patch_file_name
        self.folder = folder

        self.decomp_location = decomp_location
        self.decomp_location_with_scripts = decomp_location_with_scripts

        if scope is None:
            self.scope = Scope()

        else:
            self.scope = scope

        self.injector = BulkInjectionManager()
        self.modified_scripts = set()

    def visitAddBlockHeader(
        self: PatchfileProcessor,
        ctx: PatchfileParser.AddBlockHeaderContext
    ) -> None:
        """Add the headers to the injector metadata"""
        error_manager = ErrorManager(self.patch_file_name, ctx.start.line)
        ctx_filename = self.scope.resolve_all(ctx.FILENAME().getText(), error_manager)

        full_path = self.decomp_location_with_scripts / ctx_filename

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
        error_manager = ErrorManager(self.patch_file_name, ctx.start.line)

        for header in ctx.addBlockHeader():
            self.visitAddBlockHeader(header)

        stripped_text = self.scope.resolve_all(ctx.addBlockText().getText(), error_manager)

        if stripped_text[0] == "\n":
            stripped_text = stripped_text[1:]

        self.injector.inject(stripped_text)
        self.injector.clear()

    def visitAddAssetBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.AddAssetBlockContext
    ) -> None:
        """In an Add Asset block, we should take the specified assets and copy them into the SWF"""
        error_manager = ErrorManager(self.patch_file_name, ctx.start.line)

        local_name = self.scope.resolve_all(ctx.local.getText(), error_manager)
        remote_name = self.scope.resolve_all(ctx.swf.getText(), error_manager)

        if not Path(self.folder / local_name).exists():
            error_mesg = f"""Could not find asset: {local_name}
            Aborting..."""
            logger.exception(error_mesg)
            raise FileNotFoundError(error_mesg)

        # Create folder and copy things over
        remote_folder = remote_name.split("/")[0]

        if not (self.decomp_location / remote_folder).exists():
            Path.mkdir(self.decomp_location / remote_folder)

        shutil.copyfile(self.folder / local_name, self.decomp_location / remote_name)

        self.modified_scripts.add(self.decomp_location / remote_name)

    def visitRemoveBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.RemoveBlockContext
    ) -> None:
        """Remove is processed manually as the command is less complex than add."""
        error_manager = ErrorManager(self.patch_file_name, ctx.start.line)

        ctx_filename = self.scope.resolve_all(ctx.FILENAME().getText(), error_manager)
        full_path = self.decomp_location_with_scripts / ctx_filename

        # Open file, delete lines, and close it

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
            error_manager = ErrorManager(self.patch_file_name, i.start.line)

            ctx_filename = self.scope.resolve_all(i.FILENAME().getText(), error_manager)

            ctx_replace = self.scope.resolve_all(
                ctx.replaceBlockText().getText().strip(), error_manager
            )

            ctx_add = self.scope.resolve_all(
                ctx.addBlockText().getText().strip(), error_manager
            )

            full_path = self.decomp_location_with_scripts / ctx_filename

            current_file = read_safe(full_path, error_manager)
            updated_file, replace_location = FindContentManager(
                i.locationToken(), ctx_replace
            ).resolve(current_file, error_manager)

            injector = SingleInjectionManager(
                full_path, replace_location, full_path, i.start.line
            )

            injector.file_content = updated_file
            injector.inject(ctx_add, i.start.line)

            self.modified_scripts.add(full_path)

    def visitReplaceAllBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.ReplaceAllBlockContext
    ) -> None:
        """Replace all instances of the specified content.
        Does not support secondary commands, only direct text replacement.
        """
        error_manager = ErrorManager(self.patch_file_name, ctx.start.line)

        find_content = self.scope.resolve_all(
            ctx.replaceBlockText().getText().strip(), error_manager
        )

        replace_content = self.scope.resolve_all(
            ctx.addBlockText().getText().strip(), error_manager
        )

        for i in ctx.replaceAllBlockHeader():
            ctx_filename = self.scope.resolve_all(i.FILENAME().getText(), error_manager)
            full_path = self.decomp_location_with_scripts / ctx_filename
            error_manager = ErrorManager(self.patch_file_name, i.start.line)

            content = read_safe(full_path, error_manager)
            content = content.replace(find_content, replace_content)
            writelines_safe(full_path, [content])

            self.modified_scripts.add(full_path)

    def visitSetVarBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.SetVarBlockContext
    ) -> None:
        """Define a locally (downward-scoped only) variable."""
        self.scope.define_local(ctx.var_name.text, ctx.var_value.text)

    def visitExportVarBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.ExportVarBlockContext
    ) -> None:
        """Define a global variable."""
        self.scope.define_global(ctx.var_name.text, ctx.var_value.text)

    def visitExecPatcherBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.ExecPatcherBlockContext
    ) -> None:
        """Open and process a patch file when it is encountered."""
        error_manager = ErrorManager(self.patch_file_name, ctx.start.line)
        ctx_filename = self.scope.resolve_all(ctx.file_name().getText(), error_manager)

        # This import needs to happen here, otherwise it would cause a circular dependency
        # pylint: disable=import-outside-toplevel
        from flash_patcher.parse.patch import PatchfileManager
        patch_path = self.folder / ctx_filename
        patch_folder = patch_path.parent
        self.modified_scripts |= PatchfileManager(
            self.decomp_location,
            self.decomp_location_with_scripts,
            patch_path,
            patch_folder,
            self.scope,
        ).parse()

    def visitExecPythonBlock(
        self: PatchfileProcessor,
        ctx: PatchfileParser.ExecPythonBlockContext
    ) -> None:
        """Visit any custom .py files the user would like to execute.
        
        The python script should print out the comma-separated filenames that it modified.
        example output: "DoAction1.as,DoAction2.as"
        Python script names may not include spaces.
        """
        error_manager = ErrorManager(self.patch_file_name, ctx.start.line)
        ctx_filename = self.scope.resolve_all(ctx.file_name().getText(), error_manager)

        script_path = (self.folder / ctx_filename).resolve()
        self.modified_scripts |= get_modified_scripts_of_command(
            ["python3", script_path],
            self.decomp_location,
            self.scope,
        )

    def visitRoot(self: PatchfileProcessor, ctx: PatchfileParser.RootContext) -> set:
        """Root function. Call this when running the visitor."""
        super().visitRoot(ctx)
        return self.modified_scripts
