from __future__ import annotations

from flash_patcher.antlr_source.PatchfileParser import PatchfileParser

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.inject.location.constant_injection_location import ConstantInjectionLocation
from flash_patcher.inject.location.injection_location import InjectionLocation

class FindContentManager:
    """A class designed to find specified content within a file,
    and replace it with placeholder text.
    """

    context: PatchfileParser.LocationTokenContext = None
    search_content: str

    def __init__(
        self: FindContentManager,
        symbolic_location: PatchfileParser.LocationTokenContext,
        search_content: str,
    ) -> None:
        self.context = symbolic_location
        self.search_content = search_content

    def resolve(
        self: FindContentManager,
        file_content: str,
        exception: ErrorManager,
    ) -> (list[str], InjectionLocation):
        """Remove the specified text, and return an InjectionLocation that points to
        the location where the new content should be added.

        This will throw an exception if the instance specified is out of bounds
        (for example, requesting the 6th instance when there are only 5 in the file).

        (We don't want to do the full replacement here, because we want to process 
        secondary commands within the patch block with the SingleInjectionManager.)
        """

        split_content = file_content.split(self.search_content)
        instance_number = None

        # Integer context means Nth instance
        if isinstance(self.context, PatchfileParser.LineNumberContext):
            instance_number = int(self.context.INTEGER().getText())

        # Function context means Nth instance from the start of the function
        # We always take the first function with this name
        elif isinstance(self.context, PatchfileParser.FunctionContext):
            function_name = self.context.FUNCTION_NAME().getText()

            function_index_1 = file_content.find(f"function {function_name}")
            function_index_2 = file_content.find(f"{function_name} = function")

            if function_index_1 == -1 and function_index_2 == -1:
                exception.raise_(
                    f"""The specified function ({function_name}) could not be found!!"""
                )

            function_index = min(
                function_index_1 if function_index_1 != -1 else float('inf'),
                function_index_2 if function_index_2 != -1 else float('inf'),
            )

            # FIXME
            # Initialize a variable to keep track of the number of occurrences found
            occurrences_found = -1

            # Start searching for substring A after the first occurrence of substring B
            current_index = function_index + 1
            instance_number = int(self.context.INTEGER().getText()) or 0

            while occurrences_found <= instance_number:
                # Find the next occurrence of substring A
                current_index = file_content.find(self.search_content, current_index)

                # If no more occurrences are found, break out of the loop
                if current_index == -1:
                    break

                # Increment the count of occurrences found
                occurrences_found += 1

                # Move the current index to start searching after the current occurrence
                current_index += 1

            # If N occurrences are found, return the index of the Nth occurrence
            if occurrences_found == instance_number:
                split_content = [
                    file_content[:current_index],
                    file_content[current_index + len(self.search_content):],
                ]
                instance_number = 1
            else:
                # If less than N occurrences are found, raise an error
                exception.raise_(
                    f"""Could not find {instance_number}th instance of the content: {self.search_content}
                    with search criterion: AFTER function definition of {function_name}
                    """
                )

        # End context means the last instance
        elif isinstance(self.context, PatchfileParser.EndContext):
            instance_number = -1

        if instance_number >= len(split_content):
            exception.raise_(
                f"""Instance number {self.context.getText()} is above 
                the number of instances in the file!"""
            )

        first_section = ''.join(split_content[:instance_number]).splitlines()
        second_section = ''.join(split_content[instance_number:]).splitlines()
        split_content = first_section.extend(second_section)

        location = ConstantInjectionLocation(len(first_section))

        return split_content, location
