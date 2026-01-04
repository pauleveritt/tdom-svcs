"""
tdom-svcs processor module.

This module provides dependency injection capabilities for tdom templates
by forking tdom's html() function and intercepting component calls.
"""

import typing
from collections.abc import Mapping
from string.templatelib import Interpolation, Template

import svcs
from svcs_di.auto import get_field_infos
from svcs_di.injectors.locator import HopscotchInjector
from tdom import html as tdom_html
from tdom.callables import get_callable_info
from tdom.nodes import Comment, DocumentType, Element, Fragment, Node, Text
from tdom.parser import TComment, TComponent, TDocumentType, TElement, TFragment, TText
from tdom.processor import (
    AttributesDict,
    CachableTemplate,
    _flatten_nodes,
    _node_from_value,
    _parse_and_cache,
    _resolve_attrs,
    _resolve_ref,
    _resolve_t_attrs,
    _kebab_to_snake,
    format_interpolation,
    format_template,
)

# --------------------------------------------------------------------------
# DI Helper Functions
# --------------------------------------------------------------------------


def needs_dependency_injection(value: typing.Any) -> bool:
    """
    Check if a callable needs dependency injection.

    Returns True if the callable is a class with Inject[] fields.

    Args:
        value: The callable to check

    Returns:
        True if the callable needs DI, False otherwise
    """
    # Only classes can have Inject[] fields
    if not isinstance(value, type):
        return False

    # Check if it has any Inject[] fields
    field_infos = get_field_infos(value)
    return any(info.is_injectable for info in field_infos)




# --------------------------------------------------------------------------
# Protocols
# --------------------------------------------------------------------------


class Config(typing.Protocol):
    """
    Protocol for template processing configuration.

    Config provides optional configuration for template processing.

    The protocol enables structural subtyping - implementations don't need to
    inherit from this protocol.

    Example implementation:

        @dataclass
        class MyConfig:
            # Add configuration attributes as needed
            pass
    """

    pass  # Reserved for future configuration options


# --------------------------------------------------------------------------
# Forked Component Invocation with DI Support
# --------------------------------------------------------------------------


def _invoke_component(
    attrs: AttributesDict,
    children: list[Node],
    interpolation: Interpolation,
    config: typing.Any = None,
    context: typing.Any = None,
) -> Node:
    """
    Fork of tdom's _invoke_component with DI support.

    This function checks the context parameter for a svcs.Container. If present
    and the component needs DI, we inject dependencies. Otherwise, we
    fall through to the standard tdom behavior.

    Args:
        attrs: Component attributes from template
        children: Child nodes
        interpolation: Interpolation containing the component callable
        config: Optional config object (currently unused)
        context: Optional svcs.Container for dependency injection

    Returns:
        The rendered Node
    """
    value = format_interpolation(interpolation)

    # Check if we have a svcs.Container in context
    container: svcs.Container | None = (
        context if isinstance(context, svcs.Container) else None
    )

    # If we have a container and the component needs DI, wrap it
    if container is not None and needs_dependency_injection(value):
        # At this point, needs_dependency_injection guarantees value is a type
        assert isinstance(value, type)
        # Create HopscotchInjector which handles DI and ignores 'children' kwarg
        injector = HopscotchInjector(container=container)
        # Capture value as a type for the lambda
        cls: type = value
        # Wrapper that constructs instance via injector, then calls it if callable
        # This ensures children is passed through to __call__ method if present
        def di_callable(**kwargs: typing.Any) -> typing.Any:
            # Extract children before passing to injector (which will ignore it anyway)
            children_param = kwargs.get("children", ())
            # Construct instance with dependency injection
            instance = injector(cls, **kwargs)
            # If instance is callable and accepts children, call it with children
            if callable(instance):
                # Type narrowing for callable instance
                callable_instance = typing.cast(typing.Callable[..., typing.Any], instance)
                instance_callable_info = get_callable_info(callable_instance)
                if "children" in instance_callable_info.named_params:
                    return callable_instance(children=children_param)
                elif instance_callable_info.kwargs:
                    return callable_instance(children=children_param)
                else:
                    return callable_instance()
            return instance

        # Create new interpolation with DI wrapper
        # Preserve expression and format spec from original
        di_interpolation = Interpolation(
            di_callable,
            interpolation.expression,
            interpolation.conversion,
            interpolation.format_spec,
        )

        # Update value to the DI wrapper
        value = format_interpolation(di_interpolation)

    # Standard tdom component invocation logic (from tdom.processor._invoke_component)
    if not callable(value):
        raise TypeError(
            f"Expected a callable for component invocation, got {type(value).__name__}"
        )
    # Type narrowing: value is callable after the check
    value = typing.cast(typing.Callable[..., typing.Any], value)
    callable_info = get_callable_info(value)

    if callable_info.requires_positional:
        raise TypeError(
            "Component callables cannot have required positional arguments."
        )

    kwargs: AttributesDict = {}

    # Add all supported attributes
    for attr_name, attr_value in attrs.items():
        snake_name = _kebab_to_snake(attr_name)
        if snake_name in callable_info.named_params or callable_info.kwargs:
            kwargs[snake_name] = attr_value

    # Add children if appropriate
    if "children" in callable_info.named_params or callable_info.kwargs:
        kwargs["children"] = tuple(children)

    # Check to make sure we've fully satisfied the callable's requirements
    missing = callable_info.required_named_params - kwargs.keys()
    if missing:
        raise TypeError(
            f"Missing required parameters for component: {', '.join(missing)}"
        )

    result = value(**kwargs)
    return _node_from_value(result)


def _substitute_and_flatten_children(
    children, interpolations, config=None, context=None
):
    """
    Fork of tdom's _substitute_and_flatten_children that uses our DI-aware _resolve_t_node.

    Substitute placeholders in a list of children and flatten any fragments.
    """
    resolved = [
        _resolve_t_node(child, interpolations, config, context) for child in children
    ]
    flat = _flatten_nodes(resolved)
    return flat


def _resolve_t_text_ref(ref, interpolations):
    """Resolve a TText ref into Text or Fragment by processing interpolations."""

    if ref.is_literal:
        return Text(ref.strings[0])

    parts = [
        Text(part)
        if isinstance(part, str)
        else _node_from_value(format_interpolation(part))
        for part in _resolve_ref(ref, interpolations)
    ]

    # Flatten nodes
    flat = []
    for node in parts:
        if isinstance(node, Fragment):
            flat.extend(node.children)
        else:
            flat.append(node)

    if len(flat) == 1 and isinstance(flat[0], Text):
        return flat[0]

    return Fragment(children=flat)


def _resolve_t_node(
    t_node, interpolations: tuple[Interpolation, ...], config=None, context=None
) -> Node:
    """
    Fork of tdom's _resolve_t_node that uses our DI-aware _invoke_component.

    Resolve a TNode tree into a Node tree by processing interpolations.
    """

    match t_node:
        case TText(ref=ref):
            return _resolve_t_text_ref(ref, interpolations)
        case TComment(ref=ref):
            comment_t = _resolve_ref(ref, interpolations)
            comment = format_template(comment_t)
            return Comment(comment)
        case TDocumentType(text=text):
            return DocumentType(text)
        case TFragment(children=children):
            resolved_children = _substitute_and_flatten_children(
                children, interpolations, config, context
            )
            return Fragment(children=resolved_children)
        case TElement(tag=tag, attrs=attrs, children=children):
            resolved_attrs = _resolve_attrs(attrs, interpolations)
            resolved_children = _substitute_and_flatten_children(
                children, interpolations, config, context
            )
            return Element(tag=tag, attrs=resolved_attrs, children=resolved_children)
        case TComponent(
            start_i_index=start_i_index,
            end_i_index=end_i_index,
            attrs=t_attrs,
            children=children,
        ):
            start_interpolation = interpolations[start_i_index]
            end_interpolation = (
                None if end_i_index is None else interpolations[end_i_index]
            )
            resolved_attrs = _resolve_t_attrs(t_attrs, interpolations)
            resolved_children = _substitute_and_flatten_children(
                children, interpolations, config, context
            )
            # Validate matching start/end callables
            if (
                end_interpolation is not None
                and end_interpolation.value != start_interpolation.value
            ):
                raise TypeError("Mismatched component start and end callables.")
            # Use our DI-aware _invoke_component
            return _invoke_component(
                attrs=resolved_attrs,
                children=resolved_children,
                interpolation=start_interpolation,
                config=config,
                context=context,
            )
        case _:
            raise ValueError(f"Unknown TNode type: {type(t_node).__name__}")


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------


def html(
    template: Template,
    *,
    config: typing.Any = None,
    context: typing.Any = None,
) -> Node:
    """
    Process a template string into an HTML node tree with optional dependency injection.

    This function provides DI capabilities by passing config and context through the
    call chain to our forked _resolve_t_node. When config and context are None,
    it behaves identically to tdom's html().

    Args:
        template: A template string created with the t"" literal
        config: Optional config object (svcs.Registry or Config instance)
        context: Optional context (svcs.Container for dependency injection)

    Returns:
        A Node representing the processed HTML

    Examples:
        Basic usage (same as tdom):
        >>> node = html(t"<div>Hello</div>")

        With dependency injection:
        >>> registry = svcs.Registry()
        >>> container = svcs.Container(registry)
        >>> node = html(t"<{Button}>Click me</{Button}>", context=container)
    """
    if config is None and context is None:
        # Fast path: no DI, just use tdom directly
        return tdom_html(template)

    # Use our forked code path with DI support
    cachable = CachableTemplate(template)
    t_node = _parse_and_cache(cachable)
    return _resolve_t_node(t_node, template.interpolations, config, context)
