"""
Decorator-based per-component middleware registration for tdom-svcs.

Provides @component decorator for marking components with per-component middleware
that executes during specific lifecycle phases. Uses a dataclass-based registry
for type-safe metadata storage.

Per-component middleware executes after global middleware, with both respecting
priority ordering within their respective groups.

Usage::

    from tdom_svcs.services.middleware import component, Middleware
    from dataclasses import dataclass

    # Define middleware
    @dataclass
    class LoggingMiddleware:
        priority: int = -10

        def __call__(self, component, props, context):
            print(f"Rendering {component.__name__}")
            return props

    # Apply to component
    @component(middleware={"pre_resolution": [LoggingMiddleware()]})
    @dataclass
    class Button:
        label: str = "Click me"

    # Or use imperatively
    @dataclass
    class Card:
        title: str

    register_component(Card, middleware={"pre_resolution": [LoggingMiddleware()]})

See spec documentation for complete examples and lifecycle phase definitions.
"""

from dataclasses import dataclass, field
from typing import Callable, overload
from weakref import WeakKeyDictionary

from tdom_svcs.types import Component, MiddlewareMap

__all__ = ["component", "register_component", "get_component_middleware"]


# -------------------------------------------------------------------------
# Component Middleware Registry (Dataclass-based)
# -------------------------------------------------------------------------


@dataclass
class ComponentMetadata:
    """
    Metadata for per-component middleware configuration.

    Stores middleware organized by lifecycle phase.
    """

    middleware: MiddlewareMap = field(default_factory=dict)


# Global registry using WeakKeyDictionary to avoid memory leaks
# Components are keys, metadata are values
_component_registry: WeakKeyDictionary[Component, ComponentMetadata] = (
    WeakKeyDictionary()
)


def _store_component_middleware(
    target: Component,
    middleware: MiddlewareMap | None = None,
) -> Component:
    """
    Store middleware metadata in registry for target component.

    This function stores middleware configuration in the global registry using
    ComponentMetadata. The middleware dict maps lifecycle phases to middleware lists.

    Args:
        target: Component class or function to store metadata for
        middleware: Dict mapping lifecycle phases to middleware lists.
                   Supported phases: "pre_resolution", "post_resolution", "rendering"
                   If None, empty dict is stored.

    Returns:
        The target component unchanged (metadata stored in registry)

    Example:
        >>> @dataclass
        ... class Button:
        ...     label: str
        >>> logging_mw = LoggingMiddleware()
        >>> _store_component_middleware(Button, {"pre_resolution": [logging_mw]})
    """
    # Store middleware dict (empty if None provided)
    middleware_dict = middleware if middleware is not None else {}

    # Store in global registry
    _component_registry[target] = ComponentMetadata(middleware=middleware_dict)

    return target


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

    Args:
        target: Component class or function to decorate (when used bare)
        middleware: Dict mapping lifecycle phases to middleware lists
                   Phases: "pre_resolution", "post_resolution", "rendering"

    Returns:
        Decorated component with middleware metadata stored
    """
    if target is not None:
        return _store_component_middleware(target, middleware=None)

    def decorator(comp: Component) -> Component:
        return _store_component_middleware(comp, middleware=middleware)

    return decorator


def register_component(
    target: Component,
    middleware: MiddlewareMap | None = None,
) -> None:
    """
    Register component with per-component middleware imperatively.

    This function provides a non-decorator alternative to @component for cases
    where decorator syntax isn't suitable or preferred. It stores the same
    metadata as the decorator approach.

    Both class and function components are supported.

    Args:
        target: Component class or function to register
        middleware: Dict mapping lifecycle phases to middleware lists.
                   Supported phases: "pre_resolution", "post_resolution", "rendering"
                   If None, empty dict is stored.

    Returns:
        None (performs side effect of storing metadata on target)

    Examples:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Button:
        ...     label: str = "Click"
        >>> logging_mw = LoggingMiddleware()
        >>> register_component(Button, middleware={"pre_resolution": [logging_mw]})
        >>> get_component_middleware(Button)
        {'pre_resolution': [LoggingMiddleware(...)]}

        >>> def heading(text: str) -> str:
        ...     return f"<h1>{text}</h1>"
        >>> register_component(heading, middleware={"pre_resolution": [logging_mw]})
        >>> get_component_middleware(heading)
        {'pre_resolution': [LoggingMiddleware(...)]}
    """
    _store_component_middleware(target, middleware=middleware)


def get_component_middleware(
    component: Component,
) -> MiddlewareMap:
    """
    Retrieve per-component middleware from component registry.

    This utility function extracts the middleware dict stored by @component
    decorator or register_component() function. If no middleware is registered,
    returns an empty dict.

    Works with both decorator and imperative registration approaches.

    Args:
        component: Component class or function to retrieve middleware from

    Returns:
        Dict mapping lifecycle phases to middleware lists.
        Empty dict if no middleware registered.

    Examples:
        >>> @component(middleware={"pre_resolution": [logging_mw]})
        ... @dataclass
        ... class Button:
        ...     label: str
        >>> middleware = get_component_middleware(Button)
        >>> "pre_resolution" in middleware
        True

        >>> @dataclass
        ... class PlainComponent:
        ...     name: str
        >>> middleware = get_component_middleware(PlainComponent)
        >>> middleware
        {}
    """
    # Look up component in registry
    metadata = _component_registry.get(component)
    if metadata is not None:
        return metadata.middleware

    # No metadata - return empty dict
    return {}
