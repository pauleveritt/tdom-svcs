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

from collections import defaultdict
from dataclasses import dataclass
from pathlib import PurePath
from typing import Any

from svcs_hopscotch.middleware import get_middleware_types
from svcs_hopscotch.types import AnyMiddleware

type ComponentMap = dict[type, "ComponentInfo"]
"""Mapping from service type to its complete registration info."""


@dataclass(frozen=True)
class ComponentVariation:
    """One registered implementation of a service type, optionally specialized by resource/location."""

    implementation: type
    resource: type | None
    location: PurePath | None


@dataclass(frozen=True)
class ComponentInfo:
    """A registered service type and all its implementation variations."""

    service_type: type
    variations: tuple[ComponentVariation, ...]


@dataclass(frozen=True)
class MiddlewareInfo:
    """A registered middleware type with its default priority."""

    middleware_type: type[AnyMiddleware]
    priority: int | None


def list_components(registry: Any) -> ComponentMap:
    """Return all registered component services grouped by service type.

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
    type_map = registry.locator.as_type_map()
    grouped: defaultdict[type, list[ComponentVariation]] = defaultdict(list)

    for (service_type, _impl), reg in type_map._entries.items():
        grouped[service_type].append(
            ComponentVariation(
                implementation=reg.implementation,
                resource=reg.resource,
                location=reg.location,
            )
        )

    return {
        service_type: ComponentInfo(
            service_type=service_type,
            variations=tuple(variations),
        )
        for service_type, variations in grouped.items()
    }


def _extract_default_priority(mw_type: type[AnyMiddleware]) -> int | None:
    """Extract the default priority from a middleware's dataclass fields."""
    if not hasattr(mw_type, "__dataclass_fields__"):
        return None
    priority_field = mw_type.__dataclass_fields__.get("priority")
    if priority_field is not None and priority_field.default is not None:
        return priority_field.default
    return None


def list_middlewares(registry: Any) -> tuple[MiddlewareInfo, ...]:
    """List all registered global middleware types in the registry.

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
    return tuple(
        MiddlewareInfo(
            middleware_type=mw_type,
            priority=_extract_default_priority(mw_type),
        )
        for mw_type in get_middleware_types(registry)
    )
