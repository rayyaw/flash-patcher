from __future__ import annotations

from os import chdir
from pathlib import Path
import subprocess

from flash_patcher.antlr_source.StagefileParser import StagefileParser
from flash_patcher.antlr_source.StagefileVisitor import StagefileVisitor

from flash_patcher.parse.asset import AssetPackManager
from flash_patcher.parse.patch import PatchfileManager

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
        self.decomp_location = decomp_location.resolve()
        self.decomp_location_with_scripts = decomp_location_with_scripts.resolve()
        self.folder = folder.resolve()

        self.modified_scripts = set()

    def visitPatchFile(
        self: StagefileProcessor,
        ctx: StagefileParser.PatchFileContext
    ) -> None:
        """When we encounter a patch file, we should open and process it"""
        self.modified_scripts |= PatchfileManager(
            self.decomp_location_with_scripts, self.folder / ctx.getText()
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
        cwd = Path.cwd()
        script_path = self.folder / ctx.getText()
        chdir(self.decomp_location)
        output = subprocess.check_output(
            ["python3", script_path],
        )
        chdir(cwd)

        output = output.decode('utf-8').strip()

        if output == "":
            return

        output = output.split(",")

        for item in output:
            self.modified_scripts |= set([Path(item)])

    def visitAssetPackFile(
        self: StagefileProcessor,
        ctx: StagefileParser.AssetPackFileContext
    ) -> None:
        """When we encounter an asset pack, we should open and process it"""
        self.modified_scripts |= AssetPackManager(
            self.folder, self.decomp_location, self.folder / ctx.getText()
        ).parse()

    def visitRoot(self: StagefileProcessor, ctx: StagefileParser.RootContext) -> set[Path]:
        """Root function. Call this when running the visitor."""
        super().visitRoot(ctx)
        return self.modified_scripts
