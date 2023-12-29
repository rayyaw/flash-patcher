from __future__ import annotations

from pathlib import Path
from unittest import TestCase

from pytest import raises

from flash_patcher.antlr_source.PatchfileParser import PatchfileParser

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.exception.injection import InjectionError
from flash_patcher.inject.injection_location import InjectionLocation

# pylint: disable=wrong-import-order
from test.test_util.get_patch_context import get_add_patch_context

class InjectionLocationSpec (TestCase):

    error_manager: ErrorManager
    file_content: list[str]

    def __init__(self: InjectionLocationSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.error_manager = ErrorManager(
            "dummy_test.patch",
            -1,
        )

        with open("../test/testdata/frame_1/DoAction1.as", encoding="utf-8") as file:
            self.file_content = file.readlines()

    def get_valid_patch_context(
        self: InjectionLocationSpec,
        context_type: str,
    ) -> PatchfileParser.LocationTokenContext:
        context_map = {
            "line_no"           : 0,
            "end"               : 2,
            "function"          : 3,
            "function_offset"   : 4,
        }

        return get_add_patch_context(
            Path("../test/testdata/Patch1.patch"),
            context_map[context_type],
        )

    def get_none_patch_context(
        self: InjectionLocationSpec,
        context_type: str,
    ) -> PatchfileParser.LocationTokenContext:
        context_map = {
            "function"          : 0,
            "function_offset"   : 1,
        }

        return get_add_patch_context(
            Path("../test/testdata/Patch2.patch"),
            context_map[context_type],
        )

    def get_error_eof_patch_context(
        self: InjectionLocationSpec,
        context_type: str,
    ) -> PatchfileParser.LocationTokenContext:
        context_map = {
            "line_no"           : 2,
            "function_offset"   : 3,
        }

        return get_add_patch_context(
            Path("../test/testdata/Patch2.patch"),
            context_map[context_type],
        )

    def test_resolve_success_line_no_add(self: InjectionLocationSpec) -> None:
        line_no = InjectionLocation(self.get_valid_patch_context("line_no")) \
            .resolve(self.file_content, True, self.error_manager)

        assert line_no == 16

    def test_resolve_success_line_no_remove(self: InjectionLocationSpec) -> None:
        line_no = InjectionLocation(self.get_valid_patch_context("line_no")) \
            .resolve(self.file_content, False, self.error_manager)

        assert line_no == 17

    def test_resolve_success_function_add(self: InjectionLocationSpec) -> None:
        line_no = InjectionLocation(self.get_valid_patch_context("function")) \
            .resolve(self.file_content, True, self.error_manager)

        assert line_no == 9

    def test_resolve_success_function_remove(self: InjectionLocationSpec) -> None:
        line_no = InjectionLocation(self.get_valid_patch_context("function")) \
            .resolve(self.file_content, False, self.error_manager)

        assert line_no == 9

    def test_resolve_success_function_offset_add(self: InjectionLocationSpec) -> None:
        line_no = InjectionLocation(self.get_valid_patch_context("function_offset")) \
            .resolve(self.file_content, True, self.error_manager)

        assert line_no == 24

    def test_resolve_success_function_offset_remove(self: InjectionLocationSpec) -> None:
        line_no = InjectionLocation(self.get_valid_patch_context("function_offset")) \
            .resolve(self.file_content, False, self.error_manager)

        assert line_no == 24

    def test_resolve_success_end_add(self: InjectionLocationSpec) -> None:
        line_no = InjectionLocation(self.get_valid_patch_context("end")) \
            .resolve(self.file_content, True, self.error_manager)

        assert line_no == 69

    def test_resolve_success_end_remove(self: InjectionLocationSpec) -> None:
        line_no = InjectionLocation(self.get_valid_patch_context("end")) \
            .resolve(self.file_content, False, self.error_manager)

        assert line_no == 69

    def test_resolve_failure_invalid_command(self: InjectionLocationSpec) -> None:
        location = InjectionLocation("aeiou")

        with raises(InjectionError):
            location.resolve(self.file_content, True, self.error_manager)

    def test_resolve_none_function_offset_add(self: InjectionLocationSpec) -> None:
        line_no = InjectionLocation(self.get_none_patch_context("function_offset")) \
            .resolve(self.file_content, True, self.error_manager)

        assert line_no is None

    def test_resolve_none_function_offset_remove(self: InjectionLocationSpec) -> None:
        line_no = InjectionLocation(self.get_none_patch_context("function_offset")) \
            .resolve(self.file_content, False, self.error_manager)

        assert line_no is None

    def test_resolve_failure_line_no_beyond_eof(self: InjectionLocationSpec) -> None:
        location = InjectionLocation(self.get_error_eof_patch_context("line_no"))

        with raises(InjectionError):
            location.resolve(self.file_content, True, self.error_manager)

    def test_resolve_failure_function_offset_beyond_eof(self: InjectionLocationSpec) -> None:
        location = InjectionLocation(self.get_error_eof_patch_context("function_offset"))

        with raises(InjectionError):
            location.resolve(self.file_content, True, self.error_manager)
