"""
Decorator-based per-component middleware registration for tdom-svcs.

Provides @component decorator for marking components with per-component middleware
that executes during specific lifecycle phases. Uses registry metadata for storage.

Two-phase registration:
1. Decoration phase: @component marks the class with middleware config
2. Scanning phase: scan() discovers marked classes and registers with registry

Usage::

    from tdom_svcs.services.middleware import component
    from tdom_svcs import scan, execute_component_middleware
    from svcs_di.injectors import injectable
    from dataclasses import dataclass

    # Define middleware (must be @injectable for container resolution)
    @injectable
    @dataclass
    class LoggingMiddleware:
        priority: int = -10

        def __call__(self, component, props, context):
            print(f"Rendering {component.__name__}")
            return props

    # Apply to component with middleware TYPE (not instance)
    @component(middleware={"pre_resolution": [LoggingMiddleware]})
    @dataclass
    class Button:
        label: str = "Click me"

    # In app.py
    registry = HopscotchRegistry()
    scan(registry, my_components)  # Registers component middleware

    # Execute per-component middleware (resolves types from container)
    result = execute_component_middleware(Button, props, container, "pre_resolution")

See spec documentation for complete examples and lifecycle phase definitions.
"""

from operator import attrgetter
from typing import Any

from svcs_di.injectors import injectable

from tdom_svcs.types import Component, MiddlewareMap, Props, PropsResult

__all__ = [
    "COMPONENT_MIDDLEWARE_ATTR",
    "component",
    "execute_component_middleware",
    "register_component",
]

# Metadata attribute set by @component decorator
COMPONENT_MIDDLEWARE_ATTR = "_tdom_component_middleware_"


class component(injectable):
    """
    Decorator for marking components with per-component middleware.

    This decorator marks a class to be discovered by scan() and registered
    as a component using the "component" category. Supports optional per-component
    middleware configuration.

    Additional categories can be specified to tag components for filtering
    and organization purposes (e.g., "page", "widget", "layout").

    Supports both @component (bare) and @component(middleware={...}) syntax.
    The component is marked with metadata that scan() will discover and
    register with the registry.

    Args:
        target: Component class or function to decorate (when used bare).
        middleware: Dict mapping lifecycle phases to middleware lists.
                   Phases: "pre_resolution", "post_resolution", "rendering"
        categories: Additional categories to tag this component with.
                   The "component" category is always included.

    Returns:
        Decorated component with middleware metadata attribute.

    Example:
        >>> # Basic usage
        >>> @component(middleware={"pre_resolution": [LoggingMiddleware]})
        ... @dataclass
        ... class Button:
        ...     label: str = "Click"
        >>>
        >>> # With additional categories
        >>> @component(categories=["page", "admin"])
        ... @dataclass
        ... class AdminPage:
        ...     title: str = "Admin"
        ...     # Categories: ("component", "page", "admin")
    """

    categories = ("component",)
    _middleware_config: MiddlewareMap | None = None

    def __new__(cls, target=None, *, middleware=None, categories=None, **kwargs):
        """Create component with merged categories and middleware config."""
        # Merge default category with additional ones
        if categories:
            merged_categories = ("component",) + tuple(categories)
        else:
            merged_categories = ("component",)

        result = super().__new__(cls, target, categories=merged_categories, **kwargs)
        if isinstance(result, cls):
            result._middleware_config = middleware
        return result

    def __init__(self, target=None, *, middleware=None, categories=None, **kwargs):
        """No-op init - parameters already handled in __new__.

        This override is required to accept middleware and categories parameters
        in parameterized usage: @component(middleware={...}, categories=[...])
        """
        pass

    def post_decorate(self, target, metadata):
        """Store middleware config after decoration."""
        setattr(target, COMPONENT_MIDDLEWARE_ATTR, self._middleware_config or {})


def register_component(
    registry: Any,
    target: Component,
    middleware: MiddlewareMap | None = None,
    *,
    categories: list[str] | None = None,
) -> None:
    """Register a component imperatively with optional middleware and categories.

    This provides an imperative alternative to the @component decorator for
    cases where decoration isn't possible (dynamic registration, testing, etc.).

    Additional categories can be specified to tag components for filtering
    and organization purposes. The "component" category is always included.

    The recommended approach is to use @component decorator + scan(). Use this
    function only when you need programmatic registration.

    Args:
        registry: HopscotchRegistry to register with.
        target: Component class or function to register.
        middleware: Dict mapping lifecycle phases to middleware lists.
        categories: Additional categories to tag this component with.

    Example:
        >>> # Basic registration
        >>> register_component(registry, Button, middleware={"pre_resolution": [LogMw]})
        >>>
        >>> # With additional categories
        >>> register_component(registry, AdminPage, categories=["page", "admin"])
        >>>
        >>> # Recommended: decorator + scan
        >>> @component(middleware={"pre_resolution": [LogMw]}, categories=["page"])
        ... class Button: pass
        >>> scan(registry, my_module)
    """
    # Merge default category with additional ones
    all_categories = ["component"]
    if categories:
        all_categories.extend(categories)
    registry._register_categories(target, all_categories)
    # Register as injectable service if not already registered (allows custom factories)
    if target not in registry._services:
        registry.register_factory(target, target)
    setattr(target, COMPONENT_MIDDLEWARE_ATTR, middleware or {})




def execute_component_middleware(
    comp: Component,
    props: Props,
    container: Any,
    phase: str = "pre_resolution",
) -> PropsResult:
    """Execute per-component middleware for a lifecycle phase.

    Resolves middleware types from the container. Middleware are sorted by
    priority (lower runs first), consistent with global middleware.

    Args:
        comp: Component class or function.
        props: Current component props.
        container: DI container for resolving middleware types.
        phase: Lifecycle phase to execute (default: "pre_resolution").

    Returns:
        Modified props dict, or None if middleware halted execution.

    Example:
        >>> result = execute_middleware(Button, props, container)
        >>> result = execute_component_middleware(Button, result, container, "pre_resolution")
    """
    # Read middleware config directly from component class attribute
    mw_map = getattr(comp, COMPONENT_MIDDLEWARE_ATTR, {})
    middleware_types = mw_map.get(phase, [])

    # Resolve all types from container
    resolved = [container.get(mw_type) for mw_type in middleware_types]

    # Sort by priority (consistent with global middleware)
    sorted_middleware = sorted(resolved, key=attrgetter("priority"))

    current_props = props
    for mw_instance in sorted_middleware:
        result = mw_instance(comp, current_props, container)
        if result is None:
            return None
        current_props = result

    return current_props
