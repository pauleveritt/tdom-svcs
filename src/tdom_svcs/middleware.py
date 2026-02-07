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


class middleware(injectable):
    """Mark a class as middleware for scanning.

    This decorator marks a class to be discovered by scan() and registered
    as global middleware using the "middleware" category. The decorated class
    can be resolved from the DI container.

    Additional categories can be specified to tag middleware for filtering
    and organization purposes.

    The class must have a 'priority' attribute and be callable with
    (component, props, context) signature.

    Args:
        target: The class to decorate (when used bare).
        categories: Additional categories to tag this middleware with.
                   The "middleware" category is always included.

    Example:
        >>> # Basic usage
        >>> @middleware
        ... @dataclass
        ... class LoggingMiddleware:
        ...     priority: int = -10
        ...     def __call__(self, component, props, context):
        ...         print(f"Processing {component.__name__}")
        ...         return props
        >>>
        >>> # With additional categories
        >>> @middleware(categories=["security", "auth"])
        ... @dataclass
        ... class AuthMiddleware:
        ...     priority: int = -5
        ...     def __call__(self, component, props, context):
        ...         # Categories: ("middleware", "security", "auth")
        ...         return props
    """

    categories = ("middleware",)

    def __new__(cls, target=None, *, categories=None, **kwargs):
        """Create middleware with merged categories.

        Merges default "middleware" category with any additional categories.
        """
        # Merge default category with additional ones
        if categories:
            merged_categories = ("middleware",) + tuple(categories)
        else:
            merged_categories = ("middleware",)

        return super().__new__(cls, target, categories=merged_categories, **kwargs)

    def __init__(self, target=None, *, categories=None, **kwargs):
        """No-op init - categories already handled in __new__."""
        pass


def register_middleware(
    registry: Any,
    middleware_type: type[AnyMiddleware],
    *,
    categories: list[str] | None = None,
) -> None:
    """Register a middleware type imperatively.

    This provides an imperative alternative to the @middleware decorator for
    cases where decoration isn't possible (dynamic registration, testing, etc.).

    Additional categories can be specified to tag middleware for filtering
    and organization purposes. The "middleware" category is always included.

    The recommended approach is to use @middleware decorator + scan(). Use this
    function only when you need programmatic registration.

    Args:
        registry: HopscotchRegistry to register with.
        middleware_type: The middleware class to register.
        categories: Additional categories to tag this middleware with.

    Example:
        >>> # Basic registration
        >>> register_middleware(registry, LoggingMiddleware)
        >>>
        >>> # With additional categories
        >>> register_middleware(registry, AuthMiddleware, categories=["security", "auth"])
        >>>
        >>> # Recommended: decorator + scan
        >>> @middleware(categories=["security"])
        ... class LoggingMiddleware: pass
        >>> scan(registry, my_module)
    """
    # Merge default category with additional ones
    all_categories = ["middleware"]
    if categories:
        all_categories.extend(categories)
    registry._register_categories(middleware_type, all_categories)
    # Register as injectable service if not already registered (allows custom factories)
    if middleware_type not in registry._services:
        registry.register_factory(middleware_type, middleware_type)


def get_middleware_types(registry: Any) -> list[type[AnyMiddleware]]:
    """Get all registered middleware types from the registry.

    Args:
        registry: HopscotchRegistry to get middleware from.

    Returns:
        List of registered middleware types.
    """
    return list(registry.get_by_category("middleware"))


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
