from __future__ import annotations

import sys
from antlr4 import CommonTokenStream, InputStream
from antlr_source.StagefileLexer import StagefileLexer
from antlr_source.StagefileParser import StagefileParser
from logging import error, exception
from pathlib import Path

from parse.visitor.stage_visitor import StagefileProcessor
from util.exception import ErrorManager
from util.file_io import read_from_file

class StagefileManager:
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
        file_content = '\n'.join(read_from_file(file, error_manager))

        # FIXME - add custom error message with file name
        # FIXME - suppress bad version of ANTLR warning
        lexer = StagefileLexer(InputStream(file_content))
        parser = StagefileParser(CommonTokenStream(lexer))

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