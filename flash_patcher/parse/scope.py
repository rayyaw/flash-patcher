from __future__ import annotations

import copy
import re

from flash_patcher.exception.error_manager import ErrorManager

class Scope:
    """Maintain scope information to be used in the parser."""

    # The global scope is static, and is the same across all Scope instances.
    global_scope: dict[str, str] = {}
    local_scope: dict[str, str]

    def __init__(self: Scope, parent: Scope = None) -> None:
        if parent is None:
            self.local_scope = Scope.global_scope.copy()

        else:
            # Take keys from both local and global scopes,
            # with the specified parent scope taking priority
            self.local_scope = {**Scope.global_scope.copy(), **parent.local_scope.copy()}

    def define_local(self: Scope, var: str, value: str) -> None:
        """Define a local variable within the current scope."""
        self.local_scope[var] = value

    def define_global(self: Scope, var: str, value: str) -> None:
        """Define a global variable using the current scope."""
        self.local_scope[var] = value
        Scope.global_scope[var] = value

    def resolve(self: Scope, var: str) -> str | None:
        """Resolve the variable name into a value. Returns None if not found."""
        if var in self.local_scope:
            return self.local_scope[var]

        if var in Scope.global_scope:
            return Scope.global_scope[var]

        return None

    def resolve_all(self: Scope, content: str, error_manager: ErrorManager) -> str:
        """Resolve all instances of variables within a string,
        and return it with the content replaced.
        """
        variable_use = re.compile(r"\${.*?}")

        matches = variable_use.findall(content)

        resolved_content = content

        # We can't use match as a variable name since it's a keyword
        for matched in matches:
            matched_var_name = matched[2:-1]
            resolved_match = self.resolve(matched_var_name)

            # If the variable is not found, raise an error
            if resolved_match is None:
                error_manager.raise_(f"Undefined variable {matched}.", NameError)

            resolved_content = resolved_content.replace(matched, resolved_match)

        return resolved_content

    def get_config_map(self: Scope) -> map[str, str]:
        """Get the configuration as a map.
        This function is primarily used for subscript input.
        """
        config = copy.deepcopy(Scope.global_scope)

        for key, val in self.local_scope.items():
            config[key] = val

        return config

    def get_config(self: Scope) -> str:
        """Get the configuration in CFG format.
        This function is primarily used for subscript input.
        """
        config_map = self.get_config_map()

        config = ""

        for key, val in config_map.items():
            config += key + "=" + val + "\n"

        return config
