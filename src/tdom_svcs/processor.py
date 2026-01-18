"""
tdom-svcs processor module.

This module provides dependency injection capabilities for tdom templates
by forking several functions from tdom.processor. The forked functions add
`config` and `context` parameters that are threaded through the call chain.

FORKED FROM TDOM (../tdom/src/tdom/processor.py):
==================================================
The following functions are forks of tdom originals:

1. html() - Public API, adds config/context parameters
   - Original: tdom.processor.html() (lines 448-452)
   - Fast path delegates to tdom when no DI needed

2. _resolve_t_node() - Resolves TNode tree to Node tree
   - Original: tdom.processor._resolve_t_node() (lines 391-440)
   - Adds config/context threading through recursion

3. _substitute_and_flatten_children() - Processes child nodes
   - Original: tdom.processor._substitute_and_flatten_children() (lines 249-255)
   - Adds config/context threading

4. _invoke_component() - Invokes component callables
   - Original: tdom.processor._invoke_component() (lines 295-360)
   - Major changes: DI injection logic, class/function handling

5. _resolve_t_text_ref() - Resolves text references
   - Original: tdom.processor._resolve_t_text_ref() (lines 370-388)
   - Copied verbatim (no changes needed)

REUSED FROM TDOM (no changes):
==============================
These functions/classes are imported directly from tdom.processor:
- _flatten_nodes, _node_from_value, _parse_and_cache
- _resolve_attrs, _resolve_ref, _resolve_t_attrs
- _kebab_to_snake, format_interpolation, format_template
- AttributesDict, CachableTemplate
"""

import typing
from string.templatelib import Interpolation, Template
from typing import TypeGuard

from svcs_di.auto import get_field_infos
from svcs_di.injectors.hopscotch import HopscotchInjector
from tdom import html as tdom_html
from tdom.callables import get_callable_info
from tdom.nodes import Comment, DocumentType, Element, Fragment, Node, Text
from tdom.parser import TComment, TComponent, TDocumentType, TElement, TFragment, TText

from tdom_svcs.types import DIContainer
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
# Type Guards
# --------------------------------------------------------------------------


def is_callable_value(obj: object) -> TypeGuard[typing.Callable[..., typing.Any]]:
    """
    Type guard for callable objects.

    This function narrows the type of obj to Callable after checking,
    eliminating the need for type casts.

    Args:
        obj: Object to check

    Returns:
        True if obj is callable, False otherwise
    """
    return callable(obj)


# --------------------------------------------------------------------------
# DI Helper Functions
# --------------------------------------------------------------------------


def needs_dependency_injection(value: typing.Any) -> bool:
    """
    Check if a callable needs dependency injection.

    Uses svcs-di's get_field_infos() which handles both classes and functions.

    Args:
        value: The callable to check

    Returns:
        True if the callable has Inject[] fields/parameters, False otherwise
    """
    if not callable(value):
        return False
    # get_field_infos from svcs-di handles both classes and functions
    field_infos = get_field_infos(value)
    return any(info.is_injectable for info in field_infos)


def _is_di_container(obj: typing.Any) -> bool:
    """
    Check if obj is a proper DI container (not just a dict with .get()).

    The DIContainer protocol is @runtime_checkable, but a plain dict would
    pass isinstance() since it has a .get() method. This function explicitly
    excludes dicts to avoid false positives.

    Args:
        obj: Object to check

    Returns:
        True if obj is a DI container, False otherwise
    """
    if isinstance(obj, dict):
        return False
    return isinstance(obj, DIContainer)


def _call_instance_with_extras(
    instance: typing.Any,
    children: tuple[typing.Any, ...],
    context: typing.Any = None,
    config: typing.Any = None,
) -> typing.Any:
    """
    Call a component instance, passing children/context/config if it accepts them.

    Args:
        instance: The component instance to call
        children: Child nodes to pass if instance accepts them
        context: Optional context to pass if instance accepts it
        config: Optional config to pass if instance accepts it

    Returns:
        The result of calling the instance, or the instance itself if not callable
    """
    if not is_callable_value(instance):
        return instance

    # Type narrowed to Callable by type guard
    callable_info = get_callable_info(instance)
    kwargs: dict[str, typing.Any] = {}

    # Add context if instance accepts it
    if context is not None and (
        "context" in callable_info.named_params or callable_info.kwargs
    ):
        kwargs["context"] = context

    # Add config if instance accepts it
    if config is not None and (
        "config" in callable_info.named_params or callable_info.kwargs
    ):
        kwargs["config"] = config

    # Add children if instance accepts them
    if "children" in callable_info.named_params or callable_info.kwargs:
        kwargs["children"] = children

    return instance(**kwargs) if kwargs else instance()


# --------------------------------------------------------------------------
# FORK: _invoke_component from tdom.processor (lines 295-360)
#
# Changes from original:
# - Added `config` and `context` parameters
# - Added DI container detection via _is_di_container()
# - Added HopscotchInjector wrapping for components with Inject[] fields
# - Split handling for class components (inject then call __call__) vs
#   function components (inject and return result directly)
# - Added context/config/children passing to both __init__ and __call__
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
        context: Optional DIContainer for dependency injection

    Returns:
        The rendered Node
    """
    value = format_interpolation(interpolation)

    # Check if we have a DIContainer in context (exclude plain dicts)
    container: DIContainer | None = context if _is_di_container(context) else None

    # If we have a container and the component needs DI, wrap it
    if container is not None and needs_dependency_injection(value):
        injector = HopscotchInjector(container=container)

        if isinstance(value, type):
            # Class component: create instance via injector, then call with extras
            cls: type = value

            def inject_and_invoke(**kwargs: typing.Any) -> typing.Any:
                """Inject dependencies and invoke class component with extras."""
                extra_children = kwargs.pop("children", ())
                ctx = kwargs.pop("context", None)
                cfg = kwargs.pop("config", None)
                instance = injector(cls, **kwargs)
                return _call_instance_with_extras(
                    instance, extra_children, ctx or context, cfg or config
                )

            value = inject_and_invoke
        else:
            # Function component: inject and call directly, result is returned
            # We're in the else branch of isinstance(value, type), so it's a callable
            func = typing.cast(typing.Callable[..., typing.Any], value)

            def inject_and_call(**kwargs: typing.Any) -> typing.Any:
                """Inject dependencies and call function component."""
                # Remove special params that the injector doesn't know about
                # The function may or may not accept these - injector will validate
                kwargs.pop("children", None)
                kwargs.pop("context", None)
                kwargs.pop("config", None)
                return injector(func, **kwargs)

            value = inject_and_call

    # Standard tdom component invocation logic (from tdom.processor._invoke_component)
    if not is_callable_value(value):
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

    # For class components (types), params can go to __init__ and/or __call__
    # For function components, everything goes to the function
    is_class_component = isinstance(value, type)

    if is_class_component:
        # Class component: pass context/config/children to __init__ if it accepts them
        # Then also pass them to __call__ if it accepts them (via _call_instance_with_extras)
        if context is not None and (
            "context" in callable_info.named_params or callable_info.kwargs
        ):
            kwargs["context"] = context

        if config is not None and (
            "config" in callable_info.named_params or callable_info.kwargs
        ):
            kwargs["config"] = config

        if "children" in callable_info.named_params or callable_info.kwargs:
            kwargs["children"] = tuple(children)

        missing = callable_info.required_named_params - kwargs.keys()
        if missing:
            raise TypeError(
                f"Missing required parameters for component: {', '.join(missing)}"
            )
        instance = value(**kwargs)
        # Also pass extras to __call__ if it accepts them
        result = _call_instance_with_extras(instance, tuple(children), context, config)
    else:
        # Function component: pass everything to the function
        if context is not None and (
            "context" in callable_info.named_params or callable_info.kwargs
        ):
            kwargs["context"] = context

        if config is not None and (
            "config" in callable_info.named_params or callable_info.kwargs
        ):
            kwargs["config"] = config

        if "children" in callable_info.named_params or callable_info.kwargs:
            kwargs["children"] = tuple(children)

        missing = callable_info.required_named_params - kwargs.keys()
        if missing:
            raise TypeError(
                f"Missing required parameters for component: {', '.join(missing)}"
            )
        result = value(**kwargs)

    return _node_from_value(result)


# --------------------------------------------------------------------------
# FORK: _substitute_and_flatten_children from tdom.processor (lines 249-255)
#
# Changes from original:
# - Added `config` and `context` parameters
# - Passes config/context to _resolve_t_node() for recursive threading
# --------------------------------------------------------------------------


def _substitute_and_flatten_children(
    children: list[typing.Any],
    interpolations: tuple[Interpolation, ...],
    config: typing.Any = None,
    context: typing.Any = None,
) -> list[Node]:
    """
    Fork of tdom's _substitute_and_flatten_children that uses our DI-aware _resolve_t_node.

    Substitute placeholders in a list of children and flatten any fragments.

    Args:
        children: List of TNode children to process
        interpolations: Template interpolations
        config: Optional config object
        context: Optional svcs.Container for dependency injection

    Returns:
        Flattened list of resolved Node objects
    """
    resolved = [
        _resolve_t_node(child, interpolations, config, context) for child in children
    ]
    return _flatten_nodes(resolved)


# --------------------------------------------------------------------------
# FORK: _resolve_t_text_ref from tdom.processor (lines 370-388)
#
# Changes from original: None (verbatim copy)
# Reason for inclusion: Needed by _resolve_t_node() and not exported by tdom
# --------------------------------------------------------------------------


def _resolve_t_text_ref(
    ref: typing.Any, interpolations: tuple[Interpolation, ...]
) -> Text | Fragment:
    """
    Resolve a TText ref into Text or Fragment by processing interpolations.

    Args:
        ref: TText reference from parsed template
        interpolations: Template interpolations

    Returns:
        Text node for simple strings, Fragment for complex interpolations
    """
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


# --------------------------------------------------------------------------
# FORK: _resolve_t_node from tdom.processor (lines 391-440)
#
# Changes from original:
# - Added `config` and `context` parameters
# - Passes config/context to _substitute_and_flatten_children() calls
# - Passes config/context to _invoke_component() for TComponent handling
# --------------------------------------------------------------------------


def _resolve_t_node(
    t_node: typing.Any,
    interpolations: tuple[Interpolation, ...],
    config: typing.Any = None,
    context: typing.Any = None,
) -> Node:
    """
    Fork of tdom's _resolve_t_node that uses our DI-aware _invoke_component.

    Resolve a TNode tree into a Node tree by processing interpolations.

    Args:
        t_node: TNode from parsed template
        interpolations: Template interpolations
        config: Optional config object
        context: Optional svcs.Container for dependency injection

    Returns:
        Resolved Node
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
# FORK: html from tdom.processor (lines 448-452)
#
# Changes from original:
# - Added `config` and `context` keyword-only parameters
# - Fast path: delegates to tdom.html() when both are None
# - DI path: uses forked _resolve_t_node() to thread config/context
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
