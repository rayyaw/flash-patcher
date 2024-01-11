from __future__ import annotations

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.inject.find.find_content import FindContentManager
from flash_patcher.inject.location.constant_injection_location import ConstantInjectionLocation
from flash_patcher.inject.location.injection_location import InjectionLocation

class LastFindContentManager (FindContentManager):
    """A class designed to find specified content within a file,
    and replace it with placeholder text.
    """

    search_content: str

    def __init__(
        self: LastFindContentManager,
        search_content: str,
    ) -> None:
        self.search_content = search_content

    def resolve(
        self: LastFindContentManager,
        file_content: str,
        exception: ErrorManager,
    ) -> tuple[list[str], InjectionLocation]:
        """Remove the specified text, and return an InjectionLocation that points to
        the location where the new content should be added.

        This will throw an exception if the instance specified is out of bounds
        (for example, requesting the 6th instance when there are only 5 in the file).

        (We don't want to do the full replacement here, because we want to process 
        secondary commands within the patch block with the SingleInjectionManager.)
        """

        # Always use the last instance of the content
        current_index = file_content.rfind(self.search_content)
        occurrences_found = -1 if current_index == -1 else 0

        # If N occurrences are found, get the index of the Nth occurrence
        if occurrences_found == 0:
            split_content = [
                file_content[:current_index],
                file_content[current_index + len(self.search_content):],
            ]
        else:
            # If less than N occurrences are found, raise an error
            exception.raise_(
                f"""Could not find the last instance of the content:
                {self.search_content}
                """,
                IndexError
            )

        first_section = split_content[:1]
        second_section = split_content[1:]

        location = ConstantInjectionLocation(len(first_section))

        first_section.extend(second_section)

        return first_section, location
