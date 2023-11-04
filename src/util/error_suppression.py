import io
import sys
from logging import exception
from typing import Callable

def run_without_antlr_errors(fn: Callable[..., any]) -> any:
    """Run a command while suppressing ANTLR version mismatch warnings.
    We also want to call sys.exit() if there is a parse error, which ANTLR doesn't do.

    ANTLR does not provide an option to suppress these by default, so we need to do it manually.
    """

    # Ignore stdout, ANTLR only uses it for warnings of version mismatch
    sys_stdout_backup = sys.stdout
    sys_stderr_backup = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    output = fn()

    captured_output = sys.stderr.getvalue()

    # Restore stdout
    sys.stderr = sys_stderr_backup
    sys.stdout = sys_stdout_backup

    process_captured_output(captured_output)

    return output

def process_captured_output(captured_output = str) -> None:
    """Process the output from stderr, and error out if an error occurred."""
    if (captured_output != ""):
        exception(
            """Processing halted due to lex and parse errors.
            More info:\n%s""",
            captured_output
        )
        sys.exit(1)