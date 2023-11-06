from __future__ import annotations

from .single_injection import SingleInjectionManager

# the FilePosition should have an injectAt fn which takes lineno and lines to add and injects there
class BulkInjectionManager:
    """Handles injection of code into script files.
    
    This class will take in a list of injections and execute them.
    It should be used to parse blocks of multiple add statements, 
    as it only supports one file position per output file.

    Its contents are built as the input is parsed.
    This will only handle scripts.
    """

    injectors: list
    injected_content: list
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

    def inject(self: BulkInjectionManager) -> None:
        """Perform loaded injections."""
        if len(self.injected_content) == 0:
            return

        for injector in self.injectors:
            injector.inject(self.injected_content, self.starting_line_no)

    def inject_content(self: BulkInjectionManager, content: str) -> None:
        """Inject the content from the given string."""
        self.injected_content = content
        self.inject()

    def clear(self: BulkInjectionManager) -> None:
        """Clear all loaded content within this injector, to allow it to be used again."""
        self.injectors = []
        self.injected_content = []
        self.starting_line_no = -1
