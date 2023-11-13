from __future__ import annotations

from unittest import TestCase
from unittest.mock import MagicMock

from src.compile.compilation import CompilationManager, JPEXSInterface

class CompilationManagerSpec (TestCase):

    compilation_manager: CompilationManager

    def __init__(self: CompilationManagerSpec) -> None:
        super().__init__()
        self.compilation_manager = CompilationManager()
        self.compilation_manager.decompiler = MagicMock(JPEXSInterface)

    