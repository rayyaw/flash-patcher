from __future__ import annotations

import sys
import os
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from parse.stage import StagefileManager
from parse.visitor.stage_visitor import StagefileProcessor

class StagefileManagerSpec (TestCase):

    mock_processor: MagicMock[StagefileProcessor]
    stagefile_manager: StagefileManager

    def __init__(self: StagefileManagerSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.mock_processor = MagicMock(StagefileProcessor)

        self.stagefile_manager = StagefileManager(
            Path("../"),
            Path("test/testdata/Stage1.stage"),
            Path("./.Patcher-Temp"),
            Path("./.Patcher-Temp/scripts"),
        )

        self.stagefile_manager.stagefile_processor = self.mock_processor

    def test_parse_success(
        self: StagefileManagerSpec,
    ) -> None:
        self.stagefile_manager.parse()

        self.mock_processor.visitRoot.assert_called_once()
