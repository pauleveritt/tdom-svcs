"""Dependency injection processor for tdom templates.

Subclasses TemplateProcessor from tstring-html to add DI concerns:
- Context threading to components that accept a `context` parameter
- Inject[T] field resolution via HopscotchInjector when container is provided
- Component override lookup via _get_implementation

The container flows via the `app_state` parameter threaded by TemplateProcessor.
"""

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from string.templatelib import Template
from typing import TypeGuard

import svcs
from markupsafe import Markup
from svcs_hopscotch.auto import hopscotch_get_field_infos
from svcs_hopscotch.injectors import HopscotchInjector
from tdom.callables import get_callable_info
from tdom.parser import TAttribute
from tdom.processor import (
    ProcessContext,
    TemplateProcessor,
    _default_process_ctx,
    _resolve_t_attrs,
)

type ComponentResult = Template | str | Markup


def _is_callable(obj: object) -> TypeGuard[Callable[..., object]]:
    return callable(obj)


def needs_dependency_injection(value: object) -> bool:
    """Check if a callable has Inject[T] or Resource[T] fields/parameters."""
    if not callable(value):
        return False
    field_infos = hopscotch_get_field_infos(value)
    return any(info.is_injectable or info.is_resource for info in field_infos)


def _get_implementation(context: svcs.Container | None, cls: type) -> type:
    """Get the registered implementation for a class, or the original if none found."""
    if context is None:
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
class DIProcessorService(TemplateProcessor[svcs.Container | None]):
    """TemplateProcessor subclass that threads DI container to components."""

    def _process_component(
        self,
        template: Template,
        last_ctx: ProcessContext,
        app_state: svcs.Container | None,
        attrs: tuple[TAttribute, ...],
        start_i_index: int,
        end_i_index: int | None,
    ) -> str:
        """Invoke a component with DI container threading, injection, and override resolution."""
        children_template = self._extract_component_template(
            template, attrs, start_i_index, end_i_index, check_callables=True
        )
        raw_value = template.interpolations[start_i_index].value
        if not _is_callable(raw_value):
            raise TypeError("Component interpolation must be callable")
        component_callable = raw_value

        # --- Apply implementation override ---
        if isinstance(component_callable, type):
            component_callable = _get_implementation(app_state, component_callable)

        # --- Pre-render children template to Markup ---
        if children_template.strings == ("",):
            children_html: str | Markup = Markup("")
        else:
            children_html = Markup(
                self._process_template(children_template, last_ctx, app_state)
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
            kwargs["context"] = app_state

        # --- Invoke component (with or without DI) ---
        if needs_dependency_injection(component_callable) and app_state is not None:
            injector = HopscotchInjector(container=app_state)
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
            and _is_callable(result_t)
        ):
            sig = inspect.signature(result_t)
            call_kwargs: dict[str, object] = {}
            if "context" in sig.parameters:
                call_kwargs["context"] = app_state
            if "children" in sig.parameters:
                call_kwargs["children"] = children_html
            result_t = result_t(**call_kwargs)

        # --- Handle final result ---
        match result_t:
            case Template() if result_t.strings == ("",):
                return ""
            case Template():
                return self._process_template(result_t, last_ctx, app_state)
            case str() | Markup():
                return str(result_t)
            case _:
                raise TypeError(f"Unknown component return value: {type(result_t)}")


_di_processor = DIProcessorService(
    slash_void=True,
    uppercase_doctype=True,
)


def html(
    template: Template,
    *,
    container: svcs.Container | None = None,
) -> str | Markup:
    """Process a template string into HTML with DI support.

    Threads ``container`` to components that accept it, and resolves
    Inject[T] fields via HopscotchInjector when ``container`` is provided.

    Examples:
        >>> result = html(t"<div>Hello</div>")
    """
    return Markup(_di_processor.process(template, _default_process_ctx, container))
