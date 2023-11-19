from __future__ import annotations

import sys
from logging import exception, info
from pathlib import Path
from typing import Type

from antlr4 import CommonTokenStream, InputStream
from antlr4.Lexer import Lexer
from antlr4.Parser import Parser, ParserRuleContext

from exception_handle.error_suppression import run_without_antlr_errors
from exception_handle.error_manager import ErrorManager
from util.file_io import read_safe

class CommonParseManager:
    """Common logic for parsing any file type."""

    def parse_input(
        file_content: str,
        lexer: Type[Lexer],
        parser: Type[Parser],
    ) -> Parser:
        """Subfunction to generate a parser from file content.
        
        This needs to be a separate function to enable separate handling of ANTLR errors in it.
        """
        lexer = lexer(InputStream(file_content))
        return parser(CommonTokenStream(lexer))

    def get_root(
        lexer: Type[Lexer],
        parser: Type[Parser],

        file: Path,
    ) -> ParserRuleContext:
        """Get the root node of the syntax tree from the given file.
        
        This will automatically process all errors.
        Note that the syntax tree root within your grammar MUST have the name `root`.
        """
        info("Processing file: %s", file.as_posix())
        error_manager = ErrorManager(file.as_posix(), 0)
        file_content = read_safe(file, error_manager)

        parser = run_without_antlr_errors(
            lambda: CommonParseManager.parse_input(file_content, lexer, parser)
        )

        try:
            tree = run_without_antlr_errors(parser.root)

        # pylint: disable=broad-exception-caught
        # We want to ignore broad exception, as this should handle ANY exception thrown by ANTLR
        except Exception:
            exception(
                "Error while parsing file %s. There is likely additional logging output above.",
                file.as_posix(),
            )
            sys.exit(1)

        return tree
        