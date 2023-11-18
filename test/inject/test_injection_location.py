from __future__ import annotations

import sys
import os
from unittest import TestCase

from pytest import raises

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from exception_handle.error_manager import ErrorManager
from exception_handle.injection import InjectionError
from inject.injection_location import InjectionLocation

class InjectionLocationSpec (TestCase):

    error_manager: ErrorManager
    file_content: list[str]

    def __init__(self: InjectionLocationSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.error_manager = ErrorManager(
            "dummy_test.patch",
            -1,
        )

        with open("../test/testdata/DoAction1.as") as file:
            self.file_content = file.readlines()

    def test_resolve_success_line_no(self: InjectionLocationSpec) -> None:
        location = InjectionLocation("3")

        # InjectionLocation injects before a line, which means it subtracts 1
        assert location.line_no == 2

        line_no = location.resolve(self.file_content, self.error_manager)

        assert line_no == 2

    def test_resolve_success_end(self: InjectionLocationSpec) -> None:
        location = InjectionLocation("end")

        assert location.line_no is None
        assert location.symbolic_location == "end"

        line_no = location.resolve(self.file_content, self.error_manager)

        assert line_no == 5

    def test_resolve_failure_invalid_command(self: InjectionLocationSpec) -> None:
        location = InjectionLocation("aeiou")

        with raises(InjectionError):
            location.resolve(self.file_content, self.error_manager)

    def test_resolve_failure_line_no_beyond_eof(self: InjectionLocationSpec) -> None:
        location = InjectionLocation("99999999")

        with raises(InjectionError):
            location.resolve(self.file_content, self.error_manager)

    def test_resolve_failure_line_no_is_float(self: InjectionLocationSpec) -> None:
        location = InjectionLocation("3.2")

        with raises(InjectionError):
            location.resolve(self.file_content, self.error_manager)
