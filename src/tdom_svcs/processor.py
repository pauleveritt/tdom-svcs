"""
tdom-svcs processor module.

This module provides dependency injection capabilities for tdom templates
by wrapping tdom's html() function and intercepting component calls.
"""

import typing
from collections.abc import Mapping
from string.templatelib import Template

from tdom import html as tdom_html
from tdom.nodes import Node


class ComponentLookup(typing.Protocol):
    """
    Protocol for component lookup and resolution.

    ComponentLookup provides a pluggable interface for locating and resolving
    component callables during template processing. This enables dependency
    injection and other dynamic component resolution strategies.

    The protocol is independent of any specific DI framework and uses structural
    subtyping - implementations don't need to inherit from this protocol.

    Example implementation:

        @dataclass
        class MyComponentLookup:
            container: Any

            def __call__(
                self, name: str, context: Mapping[str, Any]
            ) -> Callable | None:
                # Look up component by name using container
                try:
                    return self.container.get(name)
                except KeyError:
                    return None

    Args:
        container: Any container object that holds component registrations.
                   The type is intentionally generic (Any) to avoid external
                   dependencies.

    Returns:
        A callable (component class or function) if found, or None to fall back
        to default component resolution.
    """

    def __init__(self, container: typing.Any) -> None: ...  # pragma: no cover

    def __call__(
        self, name: str, context: Mapping[str, typing.Any]
    ) -> typing.Callable | None: ...  # pragma: no cover


class Config(typing.Protocol):
    """
    Protocol for template processing configuration.

    Config provides optional configuration for template processing, including
    pluggable component resolution via ComponentLookup.

    The protocol enables structural subtyping - implementations don't need to
    inherit from this protocol. Any object with a component_lookup attribute
    satisfies this protocol.

    Example implementation:

        @dataclass
        class MyConfig:
            component_lookup: ComponentLookup | None = None

    Attributes:
        component_lookup: Optional ComponentLookup instance for resolving
                         components during template processing. When None,
                         templates use standard component resolution.
    """

    component_lookup: ComponentLookup | None


def html(
    template: Template,
    *,
    config: Config | None = None,
    context: Mapping[str, typing.Any] | None = None,
) -> Node:
    """
    Process a template string into an HTML node tree with optional dependency injection.

    This function wraps tdom's html() function and provides optional dependency
    injection capabilities through the config and context parameters. When these
    parameters are not provided, it behaves identically to tdom's html().

    Args:
        template: A template string created with the t"" literal
        config: Optional Config instance with component_lookup for dependency injection
        context: Optional context mapping for service resolution

    Returns:
        A Node representing the processed HTML

    Examples:
        Basic usage (same as tdom):
        >>> node = html(t"<div>Hello</div>")

        With dependency injection:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class MyConfig:
        ...     component_lookup: ComponentLookup | None = None
        >>> config = MyConfig(component_lookup=my_lookup)
        >>> node = html(t"<{Button}>Click me</{Button}>", config=config)
    """
    if config is None and context is None:
        # Fast path: no DI, just use tdom directly
        return tdom_html(template)

    # For now, we need to implement the component interception logic
    # This is a placeholder that will be expanded in future iterations
    # to actually intercept and resolve components through ComponentLookup
    return tdom_html(template)
