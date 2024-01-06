from __future__ import annotations

from unittest import TestCase

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.inject.location.constant_injection_location import ConstantInjectionLocation

class ConstantInjectionLocationSpec (TestCase):

    error_manager: ErrorManager

    def __init__(self: ConstantInjectionLocationSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.error_manager = ErrorManager(
            "dummy_test.patch",
            -1,
        )

    def test_resolve_success(self: ConstantInjectionLocationSpec) -> None:
        line_no = ConstantInjectionLocation(16) \
            .resolve([], True, self.error_manager)

        assert line_no == 16
