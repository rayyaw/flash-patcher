from __future__ import annotations

import io
import sys
from antlr4 import CommonTokenStream, InputStream
from antlr_source.StagefileLexer import StagefileLexer
from antlr_source.StagefileParser import StagefileParser
from logging import error, exception, info
from pathlib import Path

from parse.visitor.stage_visitor import StagefileProcessor
from util.error_suppression import run_without_antlr_errors, process_captured_output
from util.exception import ErrorManager
from util.file_io import read_from_file

class StagefileManager:
    def parseInput(file_content: str) -> StagefileParser:
        lexer = StagefileLexer(InputStream(file_content))
        return StagefileParser(CommonTokenStream(lexer))

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
        error_manager = ErrorManager(file.as_posix(), 0)
        # FIXME - file read should be all in one go instead of using readlines
        file_content = '\n'.join(read_from_file(file, error_manager))
        
        info("Processing file: %s", file.as_posix())
        parser = run_without_antlr_errors(lambda: StagefileManager.parseInput(file_content))

        try:
            stagefile = parser.root()

        except Exception as e:
            error(e)
            exception(
                "Error while parsing file %s. There is likely additional logging output above.",
                file.as_posix(),
            )
            sys.exit(1)

        return StagefileProcessor(
            folder,
            decomp_location,
            decomp_location_with_scripts
        ).visitRoot(stagefile)