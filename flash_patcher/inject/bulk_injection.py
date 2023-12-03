from __future__ import annotations

from flash_patcher.inject.single_injection import SingleInjectionManager

class BulkInjectionManager:
    """Handles injection of code into script files.
    
    This class will take in a list of injections and execute them.
    It should be used to parse blocks of multiple add statements, 
    as it only supports one file position per output file.

    Its contents are built as the input is parsed.
    This will only handle scripts.
    """

    injectors: list[SingleInjectionManager]
    starting_line_no: int

    def __init__(self: BulkInjectionManager) -> None:
        self.injectors = []         # List of single injectors that are primed
        self.injected_content = []   # List of lines to inject
        self.starting_line_no = -1    # The starting line (in the patchfile) of the injection

    # Return the file name of the script being modified
    def add_injection_target(
        self: BulkInjectionManager,
        target: SingleInjectionManager,
    ) -> None:
        """Add an injection target to this injector."""
        self.injectors.append(target)

    def inject(self: BulkInjectionManager, content: str) -> None:
        """Perform loaded injections."""
        for injector in self.injectors:
            injector.inject(content.splitlines(keepends=True), self.starting_line_no)

    def clear(self: BulkInjectionManager) -> None:
        """Clear all loaded content within this injector, to allow it to be used again."""
        self.injectors = []
        self.starting_line_no = -1
