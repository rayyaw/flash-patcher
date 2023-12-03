from __future__ import annotations

from pathlib import Path

from flash_patcher.antlr_source.StagefileLexer import StagefileLexer
from flash_patcher.antlr_source.StagefileParser import StagefileParser

from flash_patcher.parse.common import CommonParseManager
from flash_patcher.parse.visitor.stage_visitor import StagefileProcessor

class StagefileManager:
    """Manage stage files."""
    stagefile_processor: StagefileProcessor
    stage_file: Path

    def __init__(
        self: StagefileManager,
        folder: Path,
        file: Path,
        decomp_location: Path,
        decomp_location_with_scripts: Path,
    ) -> None:
        self.stagefile_processor = StagefileProcessor(
            folder, decomp_location, decomp_location_with_scripts
        )

        self.stage_file = folder / file

    def parse(self: StagefileManager) -> set:
        """Parse a single stagefile.
        
        This class handles everything to do with preprocessing (opening the file, etc.)
        Everything within the file will be handled by the StagefileProcessor
        """

        stagefile = CommonParseManager(StagefileLexer, StagefileParser).get_root(self.stage_file)

        return self.stagefile_processor.visitRoot(stagefile)
