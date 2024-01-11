from __future__ import annotations

from abc import ABC, abstractmethod

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.inject.location.injection_location import InjectionLocation

class FindContentManager (ABC):
    """A class designed to find specified content within a file,
    and replace it with placeholder text.
    """

    @abstractmethod
    def resolve(
        self: FindContentManager,
        file_content: str,
        exception: ErrorManager,
    ) -> tuple[list[str], InjectionLocation]:
        """Remove the specified text, and return an InjectionLocation that points to
        the location where the new content should be added.

        This should throw an exception if the instance specified is out of bounds
        (for example, requesting the 6th instance when there are only 5 in the file).

        (We don't want to do the full replacement here, because we want to process 
        secondary commands within the patch block with the SingleInjectionManager.)
        """
        raise NotImplementedError("Inherited classes must implement resolve!!")
