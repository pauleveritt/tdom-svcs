"""Protocol definition for component lookup service."""

from collections.abc import Mapping
from typing import Any, Callable, Protocol, runtime_checkable

import svcs


@runtime_checkable
class ComponentLookupProtocol(Protocol):
    """
    Protocol for component lookup and resolution.

    ComponentLookup provides a pluggable interface for locating and resolving
    component callables during template processing. This enables dependency
    injection and other dynamic component resolution strategies.

    The protocol is independent of any specific DI framework and uses structural
    subtyping - implementations don't need to inherit from this protocol.
    """

    def __init__(self, container: svcs.Container) -> None:
        """
        Initialize component lookup with a container.

        Args:
            container: svcs.Container that holds service registrations and provides
                      dependency injection capabilities.
        """
        ...

    def __call__(
        self, name: str, context: Mapping[str, Any]
    ) -> Callable | None:
        """
        Look up a component by name and construct it.

        Args:
            name: The string name of the component to resolve
            context: Context mapping for service resolution (available for future use)

        Returns:
            A callable (component class or function) if found, or None to fall back
            to default component resolution.
        """
        ...
