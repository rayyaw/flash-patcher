import sys

from pytest import raises

from flash_patcher.exception_handle.dependency import DependencyError
from flash_patcher.exception_handle.error_suppression import run_without_antlr_errors

def test_run_without_antlr_errors_success() -> None:
    run_without_antlr_errors(lambda: print("some stdout output"))

    # implicit assert_not_raised

def test_run_without_antlr_errors_failure() -> None:
    with raises(DependencyError):
        run_without_antlr_errors(lambda: sys.stderr.write("some error occurred!!"))
