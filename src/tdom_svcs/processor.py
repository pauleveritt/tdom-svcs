"""Dependency injection processor for tdom templates.

Subclasses ProcessorService from tstring-html to add DI concerns:
- Context threading to components that accept a `context` parameter
- Inject[T] field resolution via HopscotchInjector when context is a DI container
- Component override lookup via _get_implementation
- str | Markup return handling from existing tdom-svcs components

Uses a ContextVar to carry the DI container through processing (thread-safe).
"""

import inspect
from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass
from string.templatelib import Template
from typing import cast

import svcs
from markupsafe import Markup
from svcs_hopscotch.auto import hopscotch_get_field_infos
from svcs_hopscotch.injectors import HopscotchInjector
from tdom.callables import get_callable_info
from tdom.parser import TAttribute, TLiteralAttribute
from tdom.processor import (
    CachedParserService,
    ProcessContext,
    ProcessorService,
    _resolve_t_attrs,
    extract_embedded_template,
)

from tdom_svcs.types import is_di_container

type ContextArg = object | None
type ComponentResult = Template | str | Markup

_di_context: ContextVar[ContextArg] = ContextVar("_di_context", default=None)


def needs_dependency_injection(value: object) -> bool:
    """Check if a callable has Inject[T] or Resource[T] fields/parameters."""
    if not callable(value):
        return False
    field_infos = hopscotch_get_field_infos(value)
    return any(info.is_injectable or info.is_resource for info in field_infos)


def _get_implementation(context: ContextArg, cls: type) -> type:
    """Get the registered implementation for a class, or the original if none found."""
    if not is_di_container(context):
        return cls

    registry = getattr(context, "registry", None)
    if registry is None:
        return cls

    locator = getattr(registry, "locator", None)
    if locator is None:
        return cls

    get_impl = getattr(locator, "get_implementation", None)
    if get_impl is None:
        return cls

    resource = getattr(context, "resource", None)
    resource_type = type(resource) if resource is not None else None
    location = getattr(context, "location", None)

    impl = get_impl(cls, resource=resource_type, location=location)
    return impl if impl is not None else cls


@dataclass(frozen=True, kw_only=True)
class DIProcessorService(ProcessorService):
    """ProcessorService subclass that threads DI context to components."""

    def _process_component(
        self,
        template: Template,
        last_ctx: ProcessContext,
        attrs: tuple[TAttribute, ...],
        start_i_index: int,
        end_i_index: int | None,
    ) -> str:
        """Invoke a component with DI context threading, injection, and override resolution."""
        # --- Extract component callable (mirrors base class) ---
        body_start_s_index = (
            start_i_index
            + 1
            + len([1 for attr in attrs if not isinstance(attr, TLiteralAttribute)])
        )
        start_i = template.interpolations[start_i_index]
        component_callable = cast(Callable[..., object], start_i.value)

        if start_i_index != end_i_index and end_i_index is not None:
            children_template = extract_embedded_template(
                template, body_start_s_index, end_i_index
            )
            if component_callable != template.interpolations[end_i_index].value:
                raise TypeError(
                    "Component callable in start tag must match component callable in end tag."
                )
        else:
            children_template = t""

        if not callable(component_callable):
            raise TypeError("Component callable must be callable.")

        # --- DI context from ContextVar ---
        context = _di_context.get()

        # --- Apply implementation override ---
        if isinstance(component_callable, type):
            component_callable = _get_implementation(context, component_callable)

        # --- Pre-render children template to Markup ---
        if children_template.strings == ("",):
            children_html: str | Markup = Markup("")
        else:
            children_root = self.parser_api.to_tnode(children_template)
            children_html = Markup(
                self._process_tnode(children_template, last_ctx, children_root)
            )

        # --- Build kwargs from template attributes ---
        callable_info = get_callable_info(component_callable)

        if callable_info.requires_positional:
            raise TypeError(
                "Component callables cannot have required positional arguments."
            )

        resolved_attrs = _resolve_t_attrs(attrs, template.interpolations)
        kwargs: dict[str, object] = {}

        for attr_name, attr_value in resolved_attrs.items():
            snake_name = attr_name.replace("-", "_").lower()
            if snake_name in callable_info.named_params or callable_info.kwargs:
                kwargs[snake_name] = attr_value

        if "children" in callable_info.named_params or callable_info.kwargs:
            kwargs["children"] = children_html

        if "context" in callable_info.named_params or callable_info.kwargs:
            kwargs["context"] = context

        # --- Invoke component (with or without DI) ---
        result_t: object
        if needs_dependency_injection(component_callable) and is_di_container(context):
            injector = HopscotchInjector(container=cast(svcs.Container, context))
            result_t = injector(component_callable, **kwargs)
        else:
            missing = callable_info.required_named_params - kwargs.keys()
            if missing:
                raise TypeError(
                    f"Missing required parameters for component: {', '.join(missing)}"
                )
            result_t = component_callable(**kwargs)

        # --- Factory pattern: class component returns callable instance ---
        if (
            result_t is not None
            and not isinstance(result_t, Template)
            and not isinstance(result_t, (str, Markup))
            and callable(result_t)
        ):
            # It's a component instance (e.g. dataclass __call__).
            # Pass context and children to __call__ if it accepts them.
            sig = inspect.signature(result_t.__call__)
            call_kwargs: dict[str, object] = {}
            if "context" in sig.parameters:
                call_kwargs["context"] = context
            if "children" in sig.parameters:
                call_kwargs["children"] = children_html
            result_t = cast(Callable[..., object], result_t)(**call_kwargs)

        # --- Handle final result ---
        match result_t:
            case Template() if result_t.strings == ("",):
                return ""
            case Template():
                result_root = self.parser_api.to_tnode(result_t)
                return self._process_tnode(result_t, last_ctx, result_root)
            case str() | Markup():
                return str(result_t)
            case _:
                raise TypeError(f"Unknown component return value: {type(result_t)}")


_di_processor = DIProcessorService(
    parser_api=CachedParserService(),
    slash_void=True,
    uppercase_doctype=True,
)


def html(
    template: Template,
    *,
    context: ContextArg = None,
) -> str | Markup:
    """Process a template string into HTML with DI support.

    Threads ``context`` to components that accept it, and resolves
    Inject[T] fields via HopscotchInjector when ``context`` is a DI container.

    Examples:
        >>> result = html(t"<div>Hello</div>")
    """
    token = _di_context.set(context)
    try:
        return _di_processor.process_template(template)
    finally:
        _di_context.reset(token)
