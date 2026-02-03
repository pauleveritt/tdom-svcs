"""Middleware registration and execution.

This module provides global middleware management with two-phase registration:

1. **Decoration phase** (at import time):
   Use @middleware decorator to mark middleware classes.

2. **Scanning phase** (at startup):
   Use scan() to discover marked classes and register them with the registry.

3. **Execution phase** (at render time):
   Use execute_middleware() to run the middleware chain.

Example:
    # In middleware.py - mark with decorator
    @middleware
    @dataclass
    class LoggingMiddleware:
        priority: int = -10
        def __call__(self, component, props, context):
            return props

    # In app.py - scan and execute
    from tdom_svcs import scan, execute_middleware

    registry = HopscotchRegistry()
    scan(registry, my_middleware_module)

    with HopscotchContainer(registry) as container:
        result = execute_middleware(component, props, container)
"""

import inspect
from operator import attrgetter
from typing import Any, cast

from svcs_di.injectors import injectable

from tdom_svcs.types import (
    AnyMiddleware,
    Component,
    Context,
    Props,
    PropsResult,
)

# Metadata attribute set by @middleware decorator
MIDDLEWARE_METADATA_ATTR = "_tdom_middleware_"

# Registry metadata key for storing middleware types
MIDDLEWARE_REGISTRY_KEY = "tdom.middleware_types"


def middleware[T: type](cls: T) -> T:
    """Mark a class as middleware for scanning.

    This decorator marks a class to be discovered by scan() and registered
    as global middleware. It also applies @injectable so the middleware
    can be resolved from the DI container.

    The class must have a 'priority' attribute and be callable with
    (component, props, context) signature.

    Args:
        cls: The middleware class to mark.

    Returns:
        The class with middleware metadata and injectable marker.

    Example:
        >>> @middleware
        ... @dataclass
        ... class LoggingMiddleware:
        ...     priority: int = -10
        ...     def __call__(self, component, props, context):
        ...         print(f"Processing {component.__name__}")
        ...         return props
    """
    setattr(cls, MIDDLEWARE_METADATA_ATTR, True)
    # Also make it injectable so it can be resolved from container
    return injectable(cls)


def register_middleware(
    registry: Any,
    middleware_type: type[AnyMiddleware],
) -> None:
    """Register a middleware type with the registry.

    This is called by scan() for each @middleware decorated class found.
    Can also be called manually for programmatic registration.

    Args:
        registry: HopscotchRegistry to register with.
        middleware_type: The middleware class to register.

    Example:
        >>> register_middleware(registry, LoggingMiddleware)
    """
    middleware_types: list[type[AnyMiddleware]] = registry.metadata(
        MIDDLEWARE_REGISTRY_KEY, list
    )
    if middleware_type not in middleware_types:
        middleware_types.append(middleware_type)


def get_middleware_types(registry: Any) -> list[type[AnyMiddleware]]:
    """Get all registered middleware types from the registry.

    Args:
        registry: HopscotchRegistry to get middleware from.

    Returns:
        List of registered middleware types.
    """
    return registry.metadata(MIDDLEWARE_REGISTRY_KEY, list)


def _resolve_middleware(
    container: Any,
    middleware_types: list[type[AnyMiddleware]],
) -> list[AnyMiddleware]:
    """Resolve middleware types to instances from the container.

    Args:
        container: DI container to resolve middleware from.
        middleware_types: List of middleware types to resolve.

    Returns:
        List of middleware instances sorted by priority (lower first).
    """
    middleware = [container.get(t) for t in middleware_types]
    return sorted(middleware, key=attrgetter("priority"))


def execute_middleware(
    component: Component,
    props: Props,
    container: Any,
) -> PropsResult:
    """Execute middleware chain synchronously.

    Resolves all registered middleware types from the container and
    executes them in priority order (lower priority numbers first).

    Args:
        component: Component class or function being processed.
        props: Dictionary of component properties to transform.
        container: DI container (HopscotchContainer) for resolving middleware.

    Returns:
        Final transformed props dict, or None if any middleware halted execution.

    Raises:
        RuntimeError: If async middleware is detected (use execute_middleware_async).

    Example:
        >>> result = execute_middleware(MyComponent, {"key": "value"}, container)
        >>> if result is None:
        ...     print("Middleware halted execution")
    """
    middleware_types = get_middleware_types(container.registry)
    sorted_middleware = _resolve_middleware(container, middleware_types)

    current_props = props
    for mw in sorted_middleware:
        # Check if middleware is async
        if inspect.iscoroutinefunction(mw.__call__):
            raise RuntimeError(
                f"Async middleware {type(mw).__name__} detected in "
                f"synchronous execution. Use execute_middleware_async() instead."
            )

        # Cast to Context for type checking - middleware receives container as context
        result = cast(
            PropsResult, mw(component, current_props, cast(Context, container))
        )

        if result is None:
            return None

        current_props = result

    return current_props


async def execute_middleware_async(
    component: Component,
    props: Props,
    container: Any,
) -> PropsResult:
    """Execute middleware chain with async support.

    Resolves all registered middleware types from the container and
    executes them in priority order. Supports both sync and async
    middleware with automatic detection.

    Args:
        component: Component class or function being processed.
        props: Dictionary of component properties to transform.
        container: DI container (HopscotchContainer) for resolving middleware.

    Returns:
        Final transformed props dict, or None if any middleware halted execution.

    Example:
        >>> result = await execute_middleware_async(MyComponent, {"key": "value"}, container)
        >>> if result is None:
        ...     print("Middleware halted execution")
    """
    middleware_types = get_middleware_types(container.registry)
    sorted_middleware = _resolve_middleware(container, middleware_types)

    current_props = props
    # Cast to Context for type checking - middleware receives container as context
    ctx = cast(Context, container)

    for mw in sorted_middleware:
        # Check if middleware is async
        if inspect.iscoroutinefunction(mw.__call__):
            coro = mw(component, current_props, ctx)
            result = await coro  # type: ignore[misc]
        else:
            result = cast(PropsResult, mw(component, current_props, ctx))

        if result is None:
            return None

        current_props = result

    return current_props
