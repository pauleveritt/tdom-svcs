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

from collections.abc import Callable, Sequence
from string.templatelib import Interpolation, Template
from typing import cast

from svcs_di.auto import get_field_infos
from svcs_di.injectors.hopscotch import HopscotchInjector
from tdom import html as tdom_html
from tdom.callables import CallableInfo, get_callable_info
from tdom.nodes import Comment, DocumentType, Element, Fragment, Node, Text
from tdom.parser import (
    TComment,
    TComponent,
    TDocumentType,
    TElement,
    TFragment,
    TNode,
    TText,
)
from tdom.template_utils import TemplateRef

from tdom_svcs.types import is_di_container
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
# Type Aliases
# --------------------------------------------------------------------------

# Context can be a DIContainer for DI injection (svcs.Container, HopscotchContainer),
# or a Mapping for passing to components. We use object | None because static type
# checkers can't verify structural protocol satisfaction for external container types.
type ContextArg = object | None

# Config is typically a mapping of configuration values (dict, Mapping subclass).
# We use object | None for the same reason as ContextArg.
type ConfigArg = object | None


# --------------------------------------------------------------------------
# DI Helper Functions
# --------------------------------------------------------------------------


def needs_dependency_injection(value: object) -> bool:
    """
    Check if a callable needs dependency injection.

    Uses svcs-di's get_field_infos() which handles both classes and functions.

    Args:
        value: The callable to check

    Returns:
        True if the callable has Inject[] or Resource[] fields/parameters, False otherwise
    """
    if not callable(value):
        return False
    # get_field_infos from svcs-di handles both classes and functions
    field_infos = get_field_infos(value)
    return any(info.is_injectable or info.is_resource for info in field_infos)


def _add_extras_to_kwargs(
    callable_info: CallableInfo,
    kwargs: dict[str, object],
    context: ContextArg,
    config: ConfigArg,
    children: tuple[Node, ...],
) -> None:
    """Add context/config/children to kwargs if the callable accepts them."""
    if context is not None and (
        "context" in callable_info.named_params or callable_info.kwargs
    ):
        kwargs["context"] = context
    if config is not None and (
        "config" in callable_info.named_params or callable_info.kwargs
    ):
        kwargs["config"] = config
    if "children" in callable_info.named_params or callable_info.kwargs:
        kwargs["children"] = children


def _call_instance_with_extras(
    instance: object,
    children: tuple[Node, ...],
    context: ContextArg = None,
    config: ConfigArg = None,
) -> object:
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
    if not callable(instance):
        return instance

    # Use __call__ method for get_callable_info to avoid hashability issues.
    # Dataclass instances aren't hashable by default, but bound methods are.
    call_method = cast(Callable[..., object], instance.__call__)  # type: ignore[union-attr]
    callable_info = get_callable_info(call_method)
    kwargs: dict[str, object] = {}
    _add_extras_to_kwargs(callable_info, kwargs, context, config, children)

    return call_method(**kwargs) if kwargs else call_method()


# --------------------------------------------------------------------------
# FORK: _invoke_component from tdom.processor (lines 295-360)
#
# Changes from original:
# - Added `config` and `context` parameters
# - Added DI container detection via is_di_container()
# - Added HopscotchInjector wrapping for components with Inject[] fields
# - Split handling for class components (inject then call __call__) vs
#   function components (inject and return result directly)
# - Added context/config/children passing to both __init__ and __call__
# --------------------------------------------------------------------------


def _get_implementation(context: ContextArg, cls: type) -> type:
    """
    Get the registered implementation for a class from the container's locator.

    If the context is a DI container with a registry that has a locator,
    check if there's a registered implementation for the given class.
    This enables register_implementation() to override components in templates.

    Supports resource-based and location-based resolution when the container
    has resource/location attributes (e.g., HopscotchContainer).

    Args:
        context: The context (potentially a DI container)
        cls: The class to look up an implementation for

    Returns:
        The registered implementation, or the original class if none found
    """
    if not is_di_container(context):
        return cls

    # Check if context has a registry with a locator
    registry = getattr(context, "registry", None)
    if registry is None:
        return cls

    locator = getattr(registry, "locator", None)
    if locator is None:
        return cls

    # Try to get the implementation from the locator
    get_impl = getattr(locator, "get_implementation", None)
    if get_impl is None:
        return cls

    # Get resource and location from container for resource/location-based resolution
    resource = getattr(context, "resource", None)
    resource_type = type(resource) if resource is not None else None
    location = getattr(context, "location", None)

    impl = get_impl(cls, resource=resource_type, location=location)
    return impl if impl is not None else cls


def _invoke_component(
    attrs: AttributesDict,
    children: list[Node],
    interpolation: Interpolation,
    config: ConfigArg = None,
    context: ContextArg = None,
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

    # Check for registered implementation override (enables register_implementation)
    if isinstance(value, type):
        value = _get_implementation(context, value)

    # If we have a DI container in context and the component needs DI, wrap it
    # is_di_container is a TypeGuard that narrows context to DIContainer
    if is_di_container(context) and needs_dependency_injection(value):
        # HopscotchInjector expects svcs.Container; DIContainer protocol is compatible
        injector = HopscotchInjector(container=context)  # type: ignore[arg-type]

        if isinstance(value, type):
            # Class component: create instance via injector, then call with extras
            cls: type = value

            def inject_and_invoke(**kwargs: object) -> object:
                """Inject dependencies and invoke class component with extras."""
                extra_children = cast(tuple[Node, ...], kwargs.pop("children", ()))
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
            func = cast(Callable[..., object], value)

            def inject_and_call(**kwargs: object) -> object:
                """Inject dependencies and call function component."""
                # Remove special params that the injector doesn't know about
                # The function may or may not accept these - injector will validate
                kwargs.pop("children", None)
                kwargs.pop("context", None)
                kwargs.pop("config", None)
                return injector(func, **kwargs)

            value = inject_and_call

    # Standard tdom component invocation logic (from tdom.processor._invoke_component)
    if not callable(value):
        raise TypeError(
            f"Expected a callable for component invocation, got {type(value).__name__}"
        )
    value = cast(Callable[..., object], value)
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

    # Add context/config/children to kwargs if callable accepts them
    _add_extras_to_kwargs(callable_info, kwargs, context, config, tuple(children))

    missing = callable_info.required_named_params - kwargs.keys()
    if missing:
        raise TypeError(
            f"Missing required parameters for component: {', '.join(missing)}"
        )

    if is_class_component:
        instance = value(**kwargs)
        # Also pass extras to __call__ if it accepts them
        result = _call_instance_with_extras(instance, tuple(children), context, config)
    else:
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
    children: Sequence[TNode],
    interpolations: tuple[Interpolation, ...],
    config: ConfigArg = None,
    context: ContextArg = None,
) -> list[Node]:
    """
    Fork of tdom's _substitute_and_flatten_children that uses our DI-aware _resolve_t_node.

    Substitute placeholders in a list of children and flatten any fragments.

    Args:
        children: Sequence of TNode children to process
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
    ref: TemplateRef, interpolations: tuple[Interpolation, ...]
) -> Text | Fragment:
    """
    Resolve a TText ref into Text or Fragment by processing interpolations.

    Args:
        ref: TemplateRef from parsed template
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
    t_node: TNode,
    interpolations: tuple[Interpolation, ...],
    config: ConfigArg = None,
    context: ContextArg = None,
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
    config: ConfigArg = None,
    context: ContextArg = None,
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
