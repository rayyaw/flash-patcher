from __future__ import annotations

from pathlib import Path

from antlr_source.StagefileLexer import StagefileLexer
from antlr_source.StagefileParser import StagefileParser
from parse.common import CommonParseManager
from parse.visitor.stage_visitor import StagefileProcessor

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

        stagefile = CommonParseManager.get_root(StagefileLexer, StagefileParser, self.stage_file)

        return self.stagefile_processor.visitRoot(stagefile)
