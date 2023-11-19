import sys
import os

from pytest import raises

# Add the 'src' directory to the Python path
# Not doing this causes import errors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from exception_handle.dependency import DependencyError
from exception_handle.error_suppression import run_without_antlr_errors

def test_run_without_antlr_errors_success() -> None:
    run_without_antlr_errors(lambda: print("some stdout output"))

    # implicit assert_not_raised

def test_run_without_antlr_errors_failure() -> None:
    with raises(DependencyError):
        run_without_antlr_errors(lambda: sys.stderr.write("some error occurred!!"))
