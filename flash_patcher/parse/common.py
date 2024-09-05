from __future__ import annotations

from pathlib import Path
from typing import Type

from antlr4 import CommonTokenStream, InputStream
from antlr4.Lexer import Lexer
from antlr4.Parser import Parser, ParserRuleContext

from flash_patcher.exception.dependency import DependencyError
from flash_patcher.exception.error_suppression import run_without_antlr_errors
from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.util.file_io import read_safe
from flash_patcher.util.logging import logger

class CommonParseManager:
    """Common logic for parsing any file type."""

    lexer: Type[Lexer]
    parser: Type[Parser]

    def __init__(
        self: CommonParseManager,
        lexer: Type[Lexer],
        parser: Type[Parser],
    ) -> None:
        self.lexer = lexer
        self.parser = parser

    def parse_input(
        self: CommonParseManager,
        file_content: str,
    ) -> Parser:
        """Subfunction to generate a parser from file content.
        
        This needs to be a separate function to enable separate handling of ANTLR errors in it.
        """
        file_lexer = self.lexer(InputStream(file_content))
        return self.parser(CommonTokenStream(file_lexer))

    def get_root(
        self: CommonParseManager,
        file: Path,
    ) -> ParserRuleContext:
        """Get the root node of the syntax tree from the given file.
        
        This will automatically process all errors.
        Note that the syntax tree root within your grammar MUST have the name `root`.
        """
        logger.info("Processing file: %s", file.as_posix())
        error_manager = ErrorManager(file.as_posix(), 0)
        file_content = read_safe(file, error_manager)

        parser = run_without_antlr_errors(
            lambda: self.parse_input(file_content)
        )

        try:
            tree = run_without_antlr_errors(parser.root)

        # pylint: disable=broad-exception-caught
        # We want to ignore broad exception, as this should handle ANY exception thrown by ANTLR
        except Exception as exc:
            error_mesg = f"""Error while parsing file {file.as_posix()}.
            There is likely additional logging output above.
            """

            logger.exception(error_mesg)
            raise DependencyError(error_mesg) from exc

        return tree
