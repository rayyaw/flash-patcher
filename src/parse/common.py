from __future__ import annotations

import sys
from antlr4 import CommonTokenStream, InputStream
from antlr4.Lexer import Lexer
from antlr4.Parser import Parser, ParserRuleContext
from logging import error, exception, info
from pathlib import Path
from typing import Type

from util.error_suppression import run_without_antlr_errors
from util.exception import ErrorManager
from util.file_io import read_safe

class CommonParseManager:
    def parseInput(
        file_content: str,
        lexer: Type[Lexer],
        parser: Type[Parser],
    ) -> Parser:
        lexer = lexer(InputStream(file_content))
        return parser(CommonTokenStream(lexer))

    def getRoot(
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
            lambda: CommonParseManager.parseInput(file_content, lexer, parser)
        )

        try:
            tree = run_without_antlr_errors(parser.root)

        except Exception:
            exception(
                "Error while parsing file %s. There is likely additional logging output above.",
                file.as_posix(),
            )
            sys.exit(1)

        return tree
        