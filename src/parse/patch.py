from __future__ import annotations

import sys
from antlr4 import CommonTokenStream, InputStream
from antlr_source.PatchfileLexer import PatchfileLexer
from antlr_source.PatchfileParser import PatchfileParser
from logging import error, exception
from pathlib import Path

from parse.visitor.patch_visitor import PatchfileProcessor
from util.exception import ErrorManager
from util.file_io import read_from_file

class PatchfileManager:
    def parse(folder_location: Path, file_location: Path) -> set:
        """Parse a single patch file.

        folder_location: The location of the decompiled scripts from the SWF.
        file_location: The location of the patch file to apply.
        
        This class handles everything to do with preprocessing (opening the file, etc.)
        Everything within the file will be handled by the PatchfileProcessor
        Return the set of modified scripts.
        """
        file = file_location

        error_manager = ErrorManager(file.as_posix(), 0)
        # FIXME - file read should be all in one go instead of using readlines
        file_content = ''.join(read_from_file(file, error_manager))

        # FIXME - this prints an error but doesn't error out
        # FIXME - delete error message about incompatible ANTLR versions
        lexer = PatchfileLexer(InputStream(file_content))
        parser = PatchfileParser(CommonTokenStream(lexer))

        try:
            print(file.as_posix())
            stagefile = parser.root()

        except Exception as e:
            error(e)
            exception(
                "Error while parsing file %s. There is likely additional logging output above.",
                file.as_posix(),
            )
            sys.exit(1)
        
        return PatchfileProcessor(file_location, folder_location).visitRoot(stagefile)