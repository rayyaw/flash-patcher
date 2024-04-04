from __future__ import annotations

from unittest import TestCase

from pytest import raises

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.parse.scope import Scope

class ScopeSpec (TestCase):

    scope1: Scope
    scope2: Scope

    def __init__(self: ScopeSpec, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.scope1 = Scope()
        self.scope2 = Scope()

    # Use this to ensure the scope's static data is clean for the next test
    # unittest will automatically run this after every test
    def tearDown(self) -> None:
        Scope.global_scope = {}

    def test_global_scope_resolution(self: ScopeSpec) -> None:
        self.scope1.define_global("key1", "val1")

        assert self.scope1.resolve("key1") == "val1"
        assert self.scope2.resolve("key1") == "val1"

    def test_local_overrides_global_scope(self: ScopeSpec) -> None:
        self.scope1.define_global("key1", "val1")
        self.scope1.define_local("key1", "val2")

        assert self.scope1.resolve("key1") == "val2"
        assert self.scope2.resolve("key1") == "val1"

    def test_scope_resolution_not_found(self: ScopeSpec) -> None:
        assert self.scope1.resolve("key1") is None

    def test_scope_string_resolution_success(self: ScopeSpec) -> None:
        self.scope1.define_local("name", "derppotato1")
        error_manager = ErrorManager("", 1)

        assert self.scope1.resolve_all(
            r"Hello, my name is ${name}. My best friend is ${name}.", error_manager
        ) == r"Hello, my name is derppotato1. My best friend is derppotato1."

    def test_scope_string_resolution_failure_undefined(self: ScopeSpec) -> None:
        error_manager = ErrorManager("", 1)

        with raises(NameError):
            self.scope1.resolve_all(r"Hello, my name is ${name}", error_manager)

    def test_scope_creation(self: ScopeSpec) -> None:
        self.scope1.define_local("key1", "val1")

        scope3 = Scope(self.scope1)

        # Use this to ensure scope3 uses a deep copy of internal data
        self.scope1.define_local("key1", "val2")

        assert scope3.resolve("key1") == "val1"
        assert self.scope1.resolve("key1") == "val2"

    def test_get_config_map(self: ScopeSpec) -> None:
        self.scope1.define_global("key1", "val1")
        self.scope1.define_local("key1", "val2")
        self.scope1.define_global("key2", "val3")
        self.scope1.define_local("key3", "val4")

        config = self.scope1.get_config_map()

        assert "key1" in config
        assert "key2" in config
        assert "key3" in config

        assert config["key1"] == "val2"
        assert config["key2"] == "val3"
        assert config["key3"] == "val4"

    def test_get_config(self: ScopeSpec) -> None:
        self.scope1.define_global("key1", "val1")
        self.scope1.define_local("key1", "val2")
        self.scope1.define_global("key2", "val3")
        self.scope1.define_local("key3", "val4")

        config = self.scope1.get_config()

        expected_config = "key2=val3\n"
        expected_config += "key1=val2\n"
        expected_config += "key3=val4\n"

        assert config == expected_config
