from pathlib import Path
import subprocess

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if self.target_name != "wheel":
            return

        root = Path(self.root)
        grammar_dir = root / "flash_patcher" / "antlr"
        output_dir = root / "flash_patcher" / "antlr_source"

        output_dir.mkdir(parents=True, exist_ok=True)

        for grammar in ("PatchfileLexer.g4", "PatchfileParser.g4"):
            subprocess.run(
                [
                    "antlr4",
                    "-Dlanguage=Python3",
                    "-visitor",
                    "-Xexact-output-dir",
                    "-o",
                    str(output_dir),
                    str(grammar_dir / grammar),
                ],
                cwd=root,
                check=True,
            )

        # Include generated files, even if they are ignored by Git.
        build_data["artifacts"].extend([
            "flash_patcher/antlr_source/**/*.py",
            "flash_patcher/antlr_source/**/*.tokens",
            "flash_patcher/antlr_source/**/*.interp",
        ])