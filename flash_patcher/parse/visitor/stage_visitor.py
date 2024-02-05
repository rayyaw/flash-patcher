from __future__ import annotations

from pathlib import Path

from flash_patcher.antlr_source.StagefileParser import StagefileParser
from flash_patcher.antlr_source.StagefileVisitor import StagefileVisitor

from flash_patcher.parse.patch import PatchfileManager
from flash_patcher.util.external_cmd import check_output_in_dir

class StagefileProcessor (StagefileVisitor):
    """This class inherits from the ANTLR visitor to process stage files.
    
    It will automatically take in the file syntax tree 
    and perform all injections and asset adds in it.
    """

    # Folder the patch files are in
    folder: Path

    # Decomp location of SWF
    decomp_location: Path

    # Decomp location of SWF scripts
    decomp_location_with_scripts: Path

    # Set of scripts that were modified and need recompilation
    modified_scripts: set[Path]

    def __init__(
        self: StagefileProcessor,
        folder: Path,
        decomp_location: Path,
        decomp_location_with_scripts: Path
     ) -> None:
        self.decomp_location = decomp_location
        self.decomp_location_with_scripts = decomp_location_with_scripts
        self.folder = folder.resolve()

        self.modified_scripts = set()

    def visitPatchFile(
        self: StagefileProcessor,
        ctx: StagefileParser.PatchFileContext
    ) -> None:
        """When we encounter a patch file, we should open and process it"""
        self.modified_scripts |= PatchfileManager(
            self.decomp_location,
            self.decomp_location_with_scripts,
            self.folder / ctx.getText(),
            self.folder,
        ).parse()

    def visitPythonFile(
        self: StagefileProcessor,
        ctx: StagefileParser.PythonFileContext
    ) -> None:
        """Visit any custom .py files the user would like to execute.
        
        The python script should print out the comma-separated filenames that it modified.
        example output: "DoAction1.as,DoAction2.as"
        Python script names may not include spaces.
        """
        script_path = self.folder / ctx.getText()
        output = check_output_in_dir(
            ["python3", script_path],
            self.decomp_location,
        )
        output = output.decode('utf-8').strip()

        if output == "":
            return

        output = output.split(",")

        for item in output:
            self.modified_scripts.add(Path(".Patcher-Temp/mod") / item)

    def visitRoot(self: StagefileProcessor, ctx: StagefileParser.RootContext) -> set[Path]:
        """Root function. Call this when running the visitor."""
        super().visitRoot(ctx)
        return self.modified_scripts
