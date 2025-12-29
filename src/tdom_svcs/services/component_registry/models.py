"""Protocol definition for component name registry service."""

from typing import Protocol


class ComponentNameRegistryProtocol(Protocol):
    """
    Protocol for mapping component string names to class types.

    This service maintains a mapping that allows class components to be resolved by
    their string names. The registry is used by ComponentLookup to resolve
    component names from tdom templates to actual component class types that can be
    instantiated via dependency injection.

    IMPORTANT: Only class components can be registered by string name. Function
    components cannot be registered (they can still use Inject[] when called directly).
    """

    def register(self, name: str, component_type: type) -> None:
        """
        Register a component class type under a string name.

        Only class types can be registered by string name. Function components
        cannot be registered (but can still use Inject[] when called directly).

        If a component with the same name is already registered, it will be
        overwritten with the new type.

        Args:
            name: The string name to register the component under
            component_type: The component class type (must be a class)

        Raises:
            TypeError: If component_type is not a class
        """
        ...

    def get_type(self, name: str) -> type | None:
        """
        Retrieve a component class type by its registered name.

        Args:
            name: The string name of the component to look up

        Returns:
            The component class type if found, None otherwise
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
