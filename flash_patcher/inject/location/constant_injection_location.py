from __future__ import annotations

from flash_patcher.exception.error_manager import ErrorManager
from flash_patcher.inject.location.injection_location import InjectionLocation

class ConstantInjectionLocation (InjectionLocation):
    """Store the location within a file to inject at.

    This class stores a constant integer location to inject at.
    """

    location: int

    def __init__(self: ConstantInjectionLocation, location: int) -> None:
        self.location = location

    # pylint: disable=unused-argument
    # This function doesn't use the args, but they're still required
    # due to this being an overload of InjectionLocation.resolve
    def resolve(
        self: ConstantInjectionLocation,
        file_content: list[str],
        is_add: bool,
        exception: ErrorManager,
    ) -> int | None:
        """Return the stored injection location."""
        return self.location
