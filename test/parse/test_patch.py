from __future__ import annotations

from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

from flash_patcher.parse.patch import PatchfileManager
from flash_patcher.parse.patch_visitor import PatchfileProcessor

class PatchfileManagerSpec (TestCase):

    mock_processor: MagicMock[PatchfileProcessor]
    patchfile_manager: PatchfileManager

    def __init__(self: PatchfileManagerSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.mock_processor = MagicMock(PatchfileProcessor)

        self.patchfile_manager = PatchfileManager(
            Path("../"),
            Path("../"),
            Path("../test/testdata/Patch1.patch"),
            Path("../"),
        )

        self.patchfile_manager.patchfile_processor = self.mock_processor

    def test_parse_success(
        self: PatchfileManagerSpec,
    ) -> None:
        self.patchfile_manager.parse()

        self.mock_processor.visitRoot.assert_called_once()
