"""
Decorator-based per-component middleware registration for tdom-svcs.

Provides @component decorator for marking components with per-component middleware
that executes during specific lifecycle phases. The decorator stores middleware
metadata on components without performing registration, similar to @injectable.

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

from typing import Any, Callable, overload

from tdom_svcs.types import Component

from .models import Middleware

__all__ = ["component", "register_component", "get_component_middleware"]


def _store_component_middleware(
    target: Component,
    middleware: dict[str, list[Middleware]] | None = None,
) -> Component:
    """
    Store middleware metadata on target component for later retrieval.

    This function stores middleware configuration in the __tdom_svcs_middleware__
    attribute on the component. The middleware dict maps lifecycle phases to
    middleware lists.

    Args:
        target: Component class or function to store metadata on
        middleware: Dict mapping lifecycle phases to middleware lists.
                   Supported phases: "pre_resolution", "post_resolution", "rendering"
                   If None, empty dict is stored.

    Returns:
        The target component unchanged (metadata stored as side effect)

    Example:
        >>> @dataclass
        ... class Button:
        ...     label: str
        >>> logging_mw = LoggingMiddleware()
        >>> _store_component_middleware(Button, {"pre_resolution": [logging_mw]})
    """
    # Store middleware dict (empty if None provided)
    middleware_dict = middleware if middleware is not None else {}

    # Store in __tdom_svcs_middleware__ attribute
    target.__tdom_svcs_middleware__ = middleware_dict  # type: ignore[attr-defined]

    return target


class _ComponentDecorator:
    """
    Supports both @component and @component(middleware={...}) syntax.

    This decorator is similar to @injectable but adds per-component middleware
    lifecycle support. It can be used with or without parameters.
    """

    @overload
    def __call__(self, target: type) -> type: ...

    @overload
    def __call__(self, target: Callable[..., Any]) -> Callable[..., Any]: ...

    @overload
    def __call__(
        self,
        *,
        middleware: dict[str, list[Middleware]] | None = None,
    ) -> Callable[[type], type]: ...

    @overload
    def __call__(
        self,
        *,
        middleware: dict[str, list[Middleware]] | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]: ...

    def __call__(
        self,
        target: Component | None = None,
        *,
        middleware: dict[str, list[Middleware]] | None = None,
    ) -> Component:
        """
        Apply @component decorator to target component.

        This decorator stores per-component middleware metadata on the component.
        The middleware executes during specific lifecycle phases (pre_resolution,
        post_resolution, rendering) after global middleware but within the same
        priority ordering.

        Usage patterns:
            # Bare decorator on class
            @component
            @dataclass
            class Button:
                label: str = "Click"

            # Bare decorator on function
            @component
            def heading(text: str) -> str:
                return f"<h1>{text}</h1>"

            # With middleware parameter
            @component(middleware={"pre_resolution": [logging_mw]})
            @dataclass
            class Card:
                title: str

            # Multiple middleware and phases
            @component(middleware={
                "pre_resolution": [logging_mw, validation_mw],
                "post_resolution": [transform_mw],
            })
            @dataclass
            class Form:
                action: str

        Args:
            target: Component class or function to decorate (when used bare)
            middleware: Dict mapping lifecycle phases to middleware lists
                       Phases: "pre_resolution", "post_resolution", "rendering"

        Returns:
            Decorated component with middleware metadata stored

        Examples:
            >>> from dataclasses import dataclass
            >>> @component
            ... @dataclass
            ... class Button:
            ...     label: str = "Click"
            >>> hasattr(Button, "__tdom_svcs_middleware__")
            True
        """
        # Bare decorator: @component (target provided directly)
        if target is not None:
            return _store_component_middleware(target, middleware=None)

        # Called decorator: @component() or @component(middleware={...})
        def decorator(comp: Component) -> Component:
            return _store_component_middleware(comp, middleware=middleware)

        return decorator  # type: ignore[return-value]


# Create singleton decorator instance
component = _ComponentDecorator()


def register_component(
    target: Component,
    middleware: dict[str, list[Middleware]] | None = None,
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
        >>> hasattr(Button, "__tdom_svcs_middleware__")
        True

        >>> def heading(text: str) -> str:
        ...     return f"<h1>{text}</h1>"
        >>> register_component(heading, middleware={"pre_resolution": [logging_mw]})
        >>> hasattr(heading, "__tdom_svcs_middleware__")
        True
    """
    _store_component_middleware(target, middleware=middleware)


def get_component_middleware(
    component: Component,
) -> dict[str, list[Middleware]]:
    """
    Retrieve per-component middleware from component metadata.

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
    # Check if component has middleware metadata
    if hasattr(component, "__tdom_svcs_middleware__"):
        return component.__tdom_svcs_middleware__  # type: ignore[attr-defined, no-any-return]

    # No metadata - return empty dict
    return {}
