"""Registry introspection helpers for debugging and inspection.

This module provides helper functions for inspecting registered components
and middleware in a HopscotchRegistry at runtime.

Example:
    >>> from tdom_svcs import HopscotchRegistry, list_components, list_middlewares
    >>> registry = HopscotchRegistry()
    >>>
    >>> @registry.component()
    ... class Greeter:
    ...     pass
    >>>
    >>> components = list_components(registry)
    >>> Greeter in components
    True
    >>>
    >>> middlewares = list_middlewares(registry)
    >>> len(middlewares)
    0
"""

from dataclasses import dataclass
from pathlib import PurePath
from typing import Any

from svcs_hopscotch.middleware import AnyMiddleware, get_middleware_types


@dataclass(frozen=True)
class ComponentVariation:
    """Single component implementation variation.

    A variation represents one registered implementation of a component service type,
    potentially specialized for a specific resource type or location.

    Attributes:
        implementation: The implementation class or factory function.
        resource: Optional resource type this variation is specialized for.
        location: Optional location path this variation is restricted to.

    Example:
        >>> ComponentVariation(
        ...     implementation=DefaultGreeting,
        ...     resource=None,
        ...     location=None
        ... )  # doctest: +SKIP
    """

    implementation: type
    resource: type | None
    location: PurePath | None


@dataclass(frozen=True)
class ComponentInfo:
    """Complete info about a registered component service type.

    Contains the service type and all its registered implementation variations.

    Attributes:
        service_type: The service type (interface/protocol) being implemented.
        variations: Tuple of all registered implementation variations.

    Example:
        >>> ComponentInfo(
        ...     service_type=Greeting,
        ...     variations=(
        ...         ComponentVariation(DefaultGreeting, None, None),
        ...         ComponentVariation(AdminGreeting, None, PurePath("/admin")),
        ...     )
        ... )  # doctest: +SKIP
    """

    service_type: type
    variations: tuple[ComponentVariation, ...]


@dataclass(frozen=True)
class MiddlewareInfo:
    """Info about a registered global middleware type.

    Attributes:
        middleware_type: The middleware class type.
        priority: Middleware execution priority (lower executes first).

    Example:
        >>> MiddlewareInfo(
        ...     middleware_type=LoggingMiddleware,
        ...     priority=-10
        ... )  # doctest: +SKIP
    """

    middleware_type: type[AnyMiddleware]
    priority: int | None


def list_components(registry: Any) -> dict[type, ComponentInfo]:
    """List all registered component services in the registry.

    Inspects the registry's ServiceLocator to extract all registered component
    service types and their implementation variations (including resource-based
    and location-based registrations).

    Args:
        registry: HopscotchRegistry to inspect.

    Returns:
        Dictionary mapping service types to their ComponentInfo.
        Returns empty dict if no components are registered.

    Example:
        >>> from tdom_svcs import HopscotchRegistry
        >>> registry = HopscotchRegistry()
        >>>
        >>> @registry.component()
        ... class Database:
        ...     pass
        >>>
        >>> components = list_components(registry)
        >>> Database in components
        True
        >>> info = components[Database]
        >>> len(info.variations)
        1
        >>> info.variations[0].implementation is Database
        True
    """
    locator = registry.locator
    type_map = locator.as_type_map()
    result: dict[type, list[ComponentVariation]] = {}

    # Iterate through all registrations in the TypeMap
    # TypeMap stores entries keyed by (service_type, implementation)
    for (service_type, _impl), reg in type_map._entries.items():
        if service_type not in result:
            result[service_type] = []
        variation = ComponentVariation(
            implementation=reg.implementation,
            resource=reg.resource,
            location=reg.location,
        )
        result[service_type].append(variation)

    # Convert to ComponentInfo with tuples
    return {
        service_type: ComponentInfo(
            service_type=service_type,
            variations=tuple(variations),
        )
        for service_type, variations in result.items()
    }


def list_middlewares(registry: Any) -> tuple[MiddlewareInfo, ...]:
    """List all registered global middleware types in the registry.

    Uses svcs_di's get_middleware_types() to find all middleware
    registered with the "middleware" category.

    Args:
        registry: HopscotchRegistry to inspect.

    Returns:
        Tuple of MiddlewareInfo for all registered middleware.
        Returns empty tuple if no middleware are registered.

    Example:
        >>> from tdom_svcs import HopscotchRegistry
        >>> from dataclasses import dataclass
        >>>
        >>> registry = HopscotchRegistry()
        >>>
        >>> @registry.middleware
        ... @dataclass
        ... class LoggingMiddleware:
        ...     priority: int = -10
        ...     def __call__(self, component, props, context):
        ...         return props
        >>>
        >>> middlewares = list_middlewares(registry)
        >>> len(middlewares)
        1
        >>> middlewares[0].middleware_type is LoggingMiddleware
        True
        >>> middlewares[0].priority
        -10
    """
    middleware_types = get_middleware_types(registry)
    result = []

    for mw_type in middleware_types:
        # Extract default priority from dataclass field if available
        priority = None
        if hasattr(mw_type, "__dataclass_fields__"):
            priority_field = mw_type.__dataclass_fields__.get("priority")  # ty: ignore[unresolved-attribute]
            if priority_field is not None and priority_field.default is not None:
                priority = priority_field.default

        result.append(
            MiddlewareInfo(
                middleware_type=mw_type,
                priority=priority,
            )
        )

    return tuple(result)


__all__ = [
    "ComponentVariation",
    "ComponentInfo",
    "MiddlewareInfo",
    "list_components",
    "list_middlewares",
]
