from __future__ import annotations

from pathlib import Path
from unittest import TestCase

from pytest import raises

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.exception.injection import InjectionError
from flash_patcher.inject.find_content import FindContentManager
from flash_patcher.util.file_io import read_safe

# pylint: disable=wrong-import-order
from test.test_util.get_patch_context import get_add_patch_context, get_replace_patch_context

class FindContentManagerSpec (TestCase):

    file_content: str
    error_manager: ErrorManager

    def __init__(self: FindContentManagerSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.error_manager = ErrorManager(".", 0)
        self.file_content = read_safe(Path("../test/testdata/DoAction1.as"), self.error_manager)

    def test_resolve_instance_no_success(self: FindContentManagerSpec) -> None:
        context = get_replace_patch_context(Path("../test/testdata/Patch3.patch"), 2)

        data, location = FindContentManager(context, "test") \
                .resolve(self.file_content, self.error_manager)

        assert location.resolve(data, True, self.error_manager) == 1
        assert ''.join(data).count("test") == self.file_content.count("test") - 1

    def test_resolve_function_success(self: FindContentManagerSpec) -> None:
        context = get_replace_patch_context(Path("../test/testdata/Patch3.patch"), 0)

        data, location = FindContentManager(context, "test") \
                .resolve(self.file_content, self.error_manager)

        assert location.resolve(data, True, self.error_manager) == 1
        assert ''.join(data).count("test") == self.file_content.count("test") - 1

    def test_resolve_function_offset_success(self: FindContentManagerSpec) -> None:
        context = get_replace_patch_context(Path("../test/testdata/Patch3.patch"), 1)

        data, location = FindContentManager(context, "test") \
                .resolve(self.file_content, self.error_manager)

        assert location.resolve(data, True, self.error_manager) == 1
        assert ''.join(data).count("test") == self.file_content.count("test") - 1

    def test_resolve_end_success(self: FindContentManagerSpec) -> None:
        context = get_add_patch_context(Path("../test/testdata/Patch1.patch"), 2)

        data, location = FindContentManager(context, "test") \
                .resolve(self.file_content, self.error_manager)

        assert location.resolve(data, True, self.error_manager) == 1
        assert ''.join(data).count("test") == self.file_content.count("test") - 1

    def test_resolve_nth_failure_too_large(self: FindContentManagerSpec) -> None:
        context = get_add_patch_context(Path("../test/testdata/Patch1.patch"), 0)

        with raises(InjectionError):
            FindContentManager(context, "test") \
                .resolve(self.file_content, self.error_manager)

    def test_resolve_function_failure_too_large(self: FindContentManagerSpec) -> None:
        context = get_add_patch_context(Path("../test/testdata/Patch1.patch"), 1)

        with raises(InjectionError):
            FindContentManager(context, "test") \
                .resolve(self.file_content, self.error_manager)

    def test_resolve_function_failure_no_function(self: FindContentManagerSpec) -> None:
        context = get_add_patch_context(Path("../test/testdata/Patch1.patch"), 3)

        with raises(InjectionError):
            FindContentManager(context, "test") \
                .resolve(self.file_content, self.error_manager)

    def test_resolve_end_failure_no_instance(self: FindContentManagerSpec) -> None:
        context = get_add_patch_context(Path("../test/testdata/Patch1.patch"), 2)

        with raises(InjectionError):
            FindContentManager(context, "derppotato1") \
                .resolve(self.file_content, self.error_manager)

    def test_resolve_content_failure(self: FindContentManagerSpec) -> None:
        context = get_add_patch_context(Path("../test/testdata/Patch1.patch"), 5)

        with raises(InjectionError):
            FindContentManager(context, "test") \
                .resolve(self.file_content, self.error_manager)
