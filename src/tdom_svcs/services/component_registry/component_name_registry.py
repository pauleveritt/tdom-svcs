"""Implementation of component name registry service."""

import threading
from dataclasses import dataclass, field


@dataclass
class ComponentNameRegistry:
    """
    Thread-safe registry for mapping component string names to class types.

    This service maintains a dict[str, type] mapping that allows class components
    to be resolved by their string names. It's designed to be thread-safe for use
    in free-threaded Python environments.

    IMPORTANT: Only class components can be registered by string name. Function
    components cannot be registered (they can still use Inject[] when called directly).

    The registry is used by ComponentLookup to resolve component names from tdom
    templates to actual component class types that can be instantiated via dependency
    injection.

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class ButtonComponent:
        ...     label: str
        >>> registry = ComponentNameRegistry()
        >>> registry.register("Button", ButtonComponent)
        >>> component_type = registry.get_type("Button")
        >>> all_names = registry.get_all_names()
    """

    _registry: dict[str, type] = field(default_factory=dict, init=False, repr=False)
    _lock: threading.Lock = field(
        default_factory=threading.Lock, init=False, repr=False
    )

    def register(self, name: str, component_type: type) -> None:
        """
        Register a component class type under a string name.

        Only class types can be registered by string name. Function components
        cannot be registered (but can still use Inject[] when called directly).

        If a component with the same name is already registered, it will be
        overwritten with the new type.

        Args:
            name: The string name to register the component under
            component_type: The component class type to register (must be a class)

        Raises:
            TypeError: If component_type is not a class

        Example:
            >>> from dataclasses import dataclass
            >>> @dataclass
            ... class Button:
            ...     label: str
            >>> registry = ComponentNameRegistry()
            >>> registry.register("Button", Button)
        """
        # Validation: ensure it's actually a class
        if not isinstance(component_type, type):
            raise TypeError(
                f"ComponentNameRegistry only accepts class types, got {type(component_type).__name__}. "
                f"Function components can use Inject[] but cannot be registered by string name."
            )

        with self._lock:
            self._registry[name] = component_type

    def get_type(self, name: str) -> type | None:
        """
        Retrieve a component class type by its registered name.

        Args:
            name: The string name of the component to look up

        Returns:
            The component class type if found, None otherwise

        Example:
            >>> from dataclasses import dataclass
            >>> @dataclass
            ... class Button:
            ...     label: str
            >>> registry = ComponentNameRegistry()
            >>> registry.register("Button", Button)
            >>> component_type = registry.get_type("Button")
            >>> component_type is Button
            True
            >>> registry.get_type("NonExistent") is None
            True
        """
        with self._lock:
            return self._registry.get(name)

    def get_all_names(self) -> list[str]:
        """
        Get a list of all registered component names.

        This method is primarily used for generating helpful error messages
        when a component name is not found.

        Returns:
            A list of all registered component names (empty list if none registered)

        Example:
            >>> from dataclasses import dataclass
            >>> @dataclass
            ... class Button:
            ...     label: str
            >>> @dataclass
            ... class Card:
            ...     title: str
            >>> registry = ComponentNameRegistry()
            >>> registry.register("Button", Button)
            >>> registry.register("Card", Card)
            >>> sorted(registry.get_all_names())
            ['Button', 'Card']
        """
        with self._lock:
            return list(self._registry.keys())
