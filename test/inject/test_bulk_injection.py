from __future__ import annotations

from unittest import TestCase
from unittest.mock import MagicMock

from flash_patcher.inject.single_injection import SingleInjectionManager
from flash_patcher.inject.bulk_injection import BulkInjectionManager

class BulkInjectionManagerSpec (TestCase):

    bulk_injection_manager: BulkInjectionManager

    def __init__(
        self: BulkInjectionManagerSpec,
        methodName: str = "runTest",
    ) -> None:
        super().__init__(methodName)

        self.bulk_injection_manager = BulkInjectionManager()

        assert len(self.bulk_injection_manager.injectors) == 0

    def test_add_injection_target_success(self: BulkInjectionManagerSpec) -> None:
        single_injector = MagicMock(SingleInjectionManager)

        self.bulk_injection_manager.add_injection_target(single_injector)

        assert len(self.bulk_injection_manager.injectors) == 1
        assert self.bulk_injection_manager.injectors[0] == single_injector

    def test_inject_success(self: BulkInjectionManagerSpec) -> None:
        single_injector = MagicMock(SingleInjectionManager)

        self.bulk_injection_manager.add_injection_target(single_injector)
        self.bulk_injection_manager.add_injection_target(single_injector)

        self.bulk_injection_manager.inject("some test string\nwith many lines")

        assert single_injector.inject.call_count == 2
        single_injector.inject.assert_called_with(
            ["some test string\n", "with many lines"], -1
        )

    def test_clear_success(self: BulkInjectionManagerSpec) -> None:
        single_injector = MagicMock(SingleInjectionManager)

        self.bulk_injection_manager.add_injection_target(single_injector)
        self.bulk_injection_manager.clear()

        assert len(self.bulk_injection_manager.injectors) == 0
        assert self.bulk_injection_manager.starting_line_no == -1
