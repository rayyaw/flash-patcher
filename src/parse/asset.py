from __future__ import annotations

import sys
from antlr4 import CommonTokenStream, InputStream
from antlr_source.AssetPackLexer import AssetPackLexer
from antlr_source.AssetPackParser import AssetPackParser
from logging import error, exception
from pathlib import Path

from parse.visitor.asset_visitor import AssetPackProcessor
from util.exception import ErrorManager
from util.file_io import read_from_file

class AssetPackManager:
    def parse(
        decomp_location: Path,
        file: Path
    ) -> set:
        """Parse a single asset pack.
        
        This class handles everything to do with preprocessing (opening the file, etc.)
        Everything within the file will be handled by the AssetPackProcessor
        """
        error_manager = ErrorManager(file.as_posix(), 0)
        file_content = '\n'.join(read_from_file(file, error_manager))

        # FIXME - add custom error message with file name
        # FIXME - suppress bad version of ANTLR warning
        lexer = AssetPackLexer(InputStream(file_content))
        parser = AssetPackParser(CommonTokenStream(lexer))

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