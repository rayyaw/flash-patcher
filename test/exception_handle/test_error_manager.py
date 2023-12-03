from __future__ import annotations

from unittest import TestCase

from pytest import raises

from flash_patcher.exception_handle.error_manager import ErrorManager
from flash_patcher.exception_handle.injection import InjectionError

class ErrorManagerSpec (TestCase):

    error_manager: ErrorManager

    def __init__(self: ErrorManagerSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.error_manager = ErrorManager("test.patch", -1)

    def test_raise_success(self: ErrorManagerSpec) -> None:
        with raises(InjectionError):
            self.error_manager.raise_("error!")
