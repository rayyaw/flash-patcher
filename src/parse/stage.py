from __future__ import annotations

from pathlib import Path

from antlr_source.StagefileLexer import StagefileLexer
from antlr_source.StagefileParser import StagefileParser
from parse.common import CommonParseManager
from parse.visitor.stage_visitor import StagefileProcessor

class StagefileManager:
    """Manage stage files."""

    def parse(
        folder: Path,
        file: Path,
        decomp_location: Path,
        decomp_location_with_scripts: Path
    ) -> set:
        """Parse a single stagefile.
        
        This class handles everything to do with preprocessing (opening the file, etc.)
        Everything within the file will be handled by the StagefileProcessor
        """

        stagefile = CommonParseManager.get_root(StagefileLexer, StagefileParser, folder / file)

        return StagefileProcessor(
            folder,
            decomp_location,
            decomp_location_with_scripts
        ).visitRoot(stagefile)
