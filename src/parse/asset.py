from __future__ import annotations

import sys
from antlr4 import CommonTokenStream, InputStream
from antlr_source.AssetPackLexer import AssetPackLexer
from antlr_source.AssetPackParser import AssetPackParser
from logging import error, exception, info
from pathlib import Path

from parse.visitor.asset_visitor import AssetPackProcessor
from util.error_suppression import run_without_antlr_errors
from util.exception import ErrorManager
from util.file_io import read_from_file

class AssetPackManager:
    def parseInput(file_content: str) -> AssetPackParser:
        lexer = AssetPackLexer(InputStream(file_content))
        return AssetPackParser(CommonTokenStream(lexer))

    def parse(
        decomp_location: Path,
        file: Path
    ) -> set:
        """Parse a single asset pack.
        
        This class handles everything to do with preprocessing (opening the file, etc.)
        Everything within the file will be handled by the AssetPackProcessor
        """
        error_manager = ErrorManager(file.as_posix(), 0)
        # FIXME - file read should be all in one go instead of using readlines
        file_content = '\n'.join(read_from_file(file, error_manager))

        info("Processing file: %s", file.as_posix())
        parser = run_without_antlr_errors(lambda: AssetPackManager.parseInput(file_content))

        try:
            stagefile = parser.root()

        except Exception as e:
            error(e)
            exception(
                "Error while parsing file %s. There is likely additional logging output above.",
                file.as_posix(),
            )
            sys.exit(1)

        return AssetPackProcessor(decomp_location).visitRoot(stagefile)