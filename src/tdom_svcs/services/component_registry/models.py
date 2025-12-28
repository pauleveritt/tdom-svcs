"""Protocol definition for component name registry service."""

from typing import Protocol


class ComponentNameRegistryProtocol(Protocol):
    """
    Protocol for mapping component string names to type objects.

    This service maintains a mapping that allows components to be resolved by
    their string names. The registry is used by ComponentLookup to resolve
    component names from tdom templates to actual component types that can be
    instantiated via dependency injection.
    """

    def register(self, name: str, component_type: type) -> None:
        """
        Register a component type under a string name.

        If a component with the same name is already registered, it will be
        overwritten with the new type.

        Args:
            name: The string name to register the component under
            component_type: The component type (class or callable) to register
        """
        ...

    def get_type(self, name: str) -> type | None:
        """
        Retrieve a component type by its registered name.

        Args:
            name: The string name of the component to look up

        Returns:
            The component type if found, None otherwise
        """
        ...

    def get_all_names(self) -> list[str]:
        """
        Get a list of all registered component names.

        This method is primarily used for generating helpful error messages with
        suggestions when a component name is not found.

        Returns:
            A list of all registered component names (empty list if none registered)
        """
        ...
