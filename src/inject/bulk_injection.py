from __future__ import annotations

from pathlib import Path

from .single_injection import SingleInjectionManager

# the FilePosition should have an injectAt fn which takes lineno and lines to add and injects there
class BulkInjectionManager:
    """
    Handles injection of code into script files.
    This class will take in a list of injections and execute them.
    It should be used to parse blocks of multiple add statements, as it only supports one file position per output file.
    Its contents are built as the input is parsed.
    This will only handle scripts.
    """

    injectors: list
    injectedContent: list
    startingLineNo: int

    def __init__(self: BulkInjectionManager) -> None:
        self.injectors = []         # List of single injectors that are primed
        self.injectedContent = []   # List of lines to inject
        self.startingLineNo = -1    # The starting line (in the patchfile) of the injection

    # Return the file name of the script being modified
    def add_injection_target(
        self: BulkInjectionManager,
        target: SingleInjectionManager,
    ) -> None:
        """Add an injection target to this injector."""
        self.injectors.append(target)

    def add_injection_line(
        self: BulkInjectionManager,
        line: str,
        current_line_no: int,
    ) -> None:
        """Queue a line to be injected.

        The line will not be injected immediately.
        It will be injected once inject() is called.
        """
        self.injectedContent.append(line)

        if self.startingLineNo == -1:
            self.startingLineNo = current_line_no

    def inject(self: BulkInjectionManager) -> None:
        """Perform loaded injections."""
        if len(self.injectedContent) == 0:
            return
        
        for injector in self.injectors:
            injector.inject(self.injectedContent, self.startingLineNo)