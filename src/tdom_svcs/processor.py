"""Dependency injection processor for tdom templates.

Thin subclass of ComponentProcessor that adds DI concerns:
- Component override lookup via _get_implementation (overrides process())
- Inject[T] field resolution via HopscotchInjector (_invoke_component hook)

The container flows via the `app_state` parameter threaded by TemplateProcessor.
"""

from collections.abc import Callable
from dataclasses import dataclass
from string.templatelib import Template

import svcs
from svcs_hopscotch.auto import hopscotch_get_field_infos
from svcs_hopscotch.injectors import HopscotchInjector
from tdom.parser import TAttribute
from tdom.processor import (
    Attribute,
    ComponentObject,
    ComponentProcessor,
    ProcessContext,
    TemplateProcessor,
)


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
    try:
        get_impl = context.registry.locator.get_implementation  # ty: ignore[unresolved-attribute]
    except AttributeError:
        return cls
    resource = getattr(context, "resource", None)
    location = getattr(context, "location", None)
    impl = get_impl(
        cls,
        resource=type(resource) if resource is not None else None,
        location=location,
    )
    return impl if impl is not None else cls


@dataclass(frozen=True)
class DIComponentProcessor(ComponentProcessor[svcs.Container | None]):
    """ComponentProcessor subclass that adds DI injection and impl override."""

    def process(
        self,
        template: Template,
        last_ctx: ProcessContext,
        app_state: svcs.Container | None,
        component_callable: object,
        attrs: tuple[TAttribute, ...],
        component_template: Template,
        provided_attrs: tuple[Attribute, ...] = (),
    ) -> tuple[Template, ComponentObject | None]:
        if app_state is not None and isinstance(component_callable, type):
            component_callable = _get_implementation(app_state, component_callable)
        return super().process(
            template,
            last_ctx,
            app_state,
            component_callable,
            attrs,
            component_template,
            provided_attrs,
        )

    def _invoke_component(
        self,
        app_state: svcs.Container | None,
        callable_: Callable[..., object],
        kwargs: dict[str, object],
    ) -> object:
        if app_state is not None and needs_dependency_injection(callable_):
            return HopscotchInjector(container=app_state)(callable_, **kwargs)
        return callable_(**kwargs)


_tp = TemplateProcessor[svcs.Container | None](
    component_processor_api=DIComponentProcessor(),
    slash_void=True,
    uppercase_doctype=True,
)


def html(
    template: Template,
    *,
    container: svcs.Container | None = None,
) -> str:
    """Process a template string into HTML with DI support.

    Threads ``container`` to components that accept it, and resolves
    Inject[T] fields via HopscotchInjector when ``container`` is provided.

    Examples:
        >>> result = html(t"<div>Hello</div>")
    """
    return _tp.process(template, ProcessContext(), container)
