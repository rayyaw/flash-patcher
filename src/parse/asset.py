from __future__ import annotations

import shutil
import sys
from logging import exception, warning
from pathlib import Path

from util.parse import strip_line

class AssetFileParser:
    assetFile: Path
    assetFolder: Path
    decompLocation: Path

    def __init__(
        self: AssetFileParser,
        asset_file: Path,
        asset_folder: Path,
        decomp_location: Path
    ) -> None:
        
        self.assetFile = asset_file
        self.assetFolder = asset_folder
        self.decompLocation = decomp_location

        self.modifiedFiles = set()

        try:
            with Path.open(self.assetFile) as f:
                self.fileContent = f.readlines()
        except FileNotFoundError:
            exception(
                """Could not open asset pack file at: %s.
                Aborting...""",
                self.assetFile,
            )
            sys.exit(1)

    def parse(self: AssetFileParser) -> set:
        """Apply asset packs to files in a folder."""

        for line in self.fileContent:
            line_stripped = strip_line(line)
            split_line = line_stripped.split()

            if len(line_stripped) == 0 or line_stripped.startswith("#"):  
                # Lines that start with # are comments
                continue

            if line_stripped.startswith("add-asset"):
                self.parseAddAsset(split_line)

            else:
                warning("Unrecognized command: %s, skipping", line)

        return self.modifiedFiles
    
    def parseAddAsset(self: AssetFileParser, split_line: list) -> None:
        """Parse an add-asset command."""
        # Local copy of file, then remote
        local_name = split_line[1]
        remote_name = " ".join(split_line[2:])

        if not Path(self.assetFolder / local_name).exists():
            exception(
                """Could not find asset: %s
                Aborting...""",
                local_name,
            )
            sys.exit(1)

        # Create folder and copy things over
        remote_folder = remote_name.split("/")[0]

        if not (self.decompLocation / remote_folder).exists():
            Path.mkdir(self.decompLocation / remote_folder)

        shutil.copyfile(self.assetFolder / local_name, self.decompLocation / remote_name)

        self.modifiedFiles.add(self.decompLocation / remote_name)