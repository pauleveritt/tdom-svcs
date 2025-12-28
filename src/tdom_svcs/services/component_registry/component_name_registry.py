"""Implementation of component name registry service."""

import threading
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class ComponentNameRegistry:
    """
    Thread-safe registry for mapping component string names to type objects.

    This service maintains a dict[str, type] mapping that allows components to be
    resolved by their string names. It's designed to be thread-safe for use in
    free-threaded Python environments.

    The registry is used by ComponentLookup to resolve component names from tdom
    templates to actual component types that can be instantiated via dependency
    injection.

    Example:
        >>> registry = ComponentNameRegistry()
        >>> registry.register("Button", ButtonComponent)
        >>> component_type = registry.get_type("Button")
        >>> all_names = registry.get_all_names()  # For error suggestions
    """

    _registry: dict[str, type | Callable] = field(default_factory=dict, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def register(self, name: str, component_type: type | Callable) -> None:
        """
        Register a component type under a string name.

        If a component with the same name is already registered, it will be
        overwritten with the new type.

        Args:
            name: The string name to register the component under
            component_type: The component type (class or callable) to register

        Example:
            >>> registry = ComponentNameRegistry()
            >>> def Button(*, label: str = "Click"): pass
            >>> registry.register("Button", Button)
        """
        with self._lock:
            self._registry[name] = component_type

    def get_type(self, name: str) -> type | Callable | None:
        """
        Retrieve a component type by its registered name.

        Args:
            name: The string name of the component to look up

        Returns:
            The component type if found, None otherwise

        Example:
            >>> registry = ComponentNameRegistry()
            >>> def Button(*, label: str = "Click"): pass
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

        This method is primarily used for generating helpful error messages with
        suggestions when a component name is not found.

        Returns:
            A list of all registered component names (empty list if none registered)

        Example:
            >>> registry = ComponentNameRegistry()
            >>> registry.register("Button", lambda: None)
            >>> registry.register("Card", lambda: None)
            >>> sorted(registry.get_all_names())
            ['Button', 'Card']
        """
        with self._lock:
            return list(self._registry.keys())
