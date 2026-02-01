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
from typing import Any, Callable, overload

from svcs_di.injectors import injectable

from tdom_svcs.types import Component, MiddlewareMap, Props, PropsResult

__all__ = [
    "COMPONENT_MIDDLEWARE_ATTR",
    "component",
    "execute_component_middleware",
    "register_component",
    "register_component_middleware",
    "get_component_middleware",
]

# Metadata attribute set by @component decorator
COMPONENT_MIDDLEWARE_ATTR = "_tdom_component_middleware_"

# Registry metadata key for storing component middleware
COMPONENT_MW_REGISTRY_KEY = "tdom.component_middleware"


def _mark_component(
    target: Component,
    middleware: MiddlewareMap | None = None,
) -> Component:
    """
    Mark a component with middleware metadata attribute.

    This stores the middleware config on the class itself. The scan()
    function will find this and register it with the registry.
    Also applies @injectable so the component can be resolved from DI.

    Args:
        target: Component class or function to mark.
        middleware: Dict mapping lifecycle phases to middleware lists.

    Returns:
        The target component with metadata attribute set and injectable marker.
    """
    middleware_dict = middleware if middleware is not None else {}
    setattr(target, COMPONENT_MIDDLEWARE_ATTR, middleware_dict)
    # Also make it injectable so it can be resolved from container
    return injectable(target)


@overload
def component(target: Component) -> Component:
    """Bare decorator usage: @component"""
    ...


@overload
def component(
    *,
    middleware: MiddlewareMap | None = None,
) -> Callable[[Component], Component]:
    """Parametrized decorator usage: @component(middleware={...})"""
    ...


def component(
    target: Component | None = None,
    *,
    middleware: MiddlewareMap | None = None,
) -> Component | Callable[[Component], Component]:
    """
    Decorator for marking components with per-component middleware.

    Supports both @component (bare) and @component(middleware={...}) syntax.
    The component is marked with metadata that scan() will discover and
    register with the registry.

    Args:
        target: Component class or function to decorate (when used bare).
        middleware: Dict mapping lifecycle phases to middleware lists.
                   Phases: "pre_resolution", "post_resolution", "rendering"

    Returns:
        Decorated component with middleware metadata attribute.

    Example:
        >>> @component(middleware={"pre_resolution": [LoggingMiddleware]})
        ... @dataclass
        ... class Button:
        ...     label: str = "Click"
    """
    if target is not None:
        return _mark_component(target, middleware=None)

    def decorator(comp: Component) -> Component:
        return _mark_component(comp, middleware=middleware)

    return decorator


def register_component(
    target: Component,
    middleware: MiddlewareMap | None = None,
) -> None:
    """
    Mark a component with per-component middleware imperatively.

    This function provides a non-decorator alternative to @component.
    The component is marked with metadata that scan() will discover.

    Args:
        target: Component class or function to mark.
        middleware: Dict mapping lifecycle phases to middleware lists.

    Example:
        >>> register_component(Button, middleware={"pre_resolution": [LoggingMiddleware]})
    """
    _mark_component(target, middleware=middleware)


def register_component_middleware(
    registry: Any,
    target: Component,
    middleware: MiddlewareMap,
) -> None:
    """
    Register component middleware with the registry.

    This is called by scan() for each @component decorated class found.
    Can also be called manually for programmatic registration.

    Args:
        registry: HopscotchRegistry to register with.
        target: Component class or function.
        middleware: Dict mapping lifecycle phases to middleware lists.
    """
    component_mw: dict[Component, MiddlewareMap] = registry.metadata(
        COMPONENT_MW_REGISTRY_KEY, dict
    )
    component_mw[target] = middleware


def get_component_middleware(
    registry: Any,
    comp: Component,
) -> MiddlewareMap:
    """
    Retrieve per-component middleware from registry.

    Args:
        registry: HopscotchRegistry to get middleware from.
        comp: Component class or function to retrieve middleware for.

    Returns:
        Dict mapping lifecycle phases to middleware lists.
        Empty dict if no middleware registered.

    Example:
        >>> mw = get_component_middleware(registry, Button)
        >>> pre_mw = mw.get("pre_resolution", [])
    """
    component_mw: dict[Component, MiddlewareMap] = registry.metadata(
        COMPONENT_MW_REGISTRY_KEY, dict
    )
    return component_mw.get(comp, {})


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
    registry = container.registry
    mw_map = get_component_middleware(registry, comp)
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
