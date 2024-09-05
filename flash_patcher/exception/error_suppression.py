import io
import sys
from typing import Callable

from flash_patcher.exception.dependency import DependencyError
from flash_patcher.util.logging import logger

def run_without_antlr_errors(function: Callable[..., any]) -> any:
    """Run a command while suppressing ANTLR version mismatch warnings.
    We also want to raise an exception if there is a parse error, which ANTLR doesn't do.

    ANTLR does not provide an option to suppress these by default, so we need to do it manually.
    """

    # Ignore stdout, ANTLR only uses it for warnings of version mismatch
    sys_stdout_backup = sys.stdout
    sys_stderr_backup = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()

    output = function()

    captured_output = sys.stderr.getvalue()

    # Restore stdout
    sys.stderr = sys_stderr_backup
    sys.stdout = sys_stdout_backup

    process_captured_output(captured_output)

    return output

def process_captured_output(captured_output = str) -> None:
    """Process the output from stderr, and error out if an error occurred."""
    if captured_output != "":
        error_mesg = f"""Processing halted due to lex and parse errors.
            More info:\n{captured_output}"""
        logger.error(error_mesg)
        raise DependencyError(error_mesg)
