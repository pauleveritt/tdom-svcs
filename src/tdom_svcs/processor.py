"""Dependency injection processor for tdom templates.

Option C architecture: resolves DI fields through Hopscotch's full pipeline,
then delegates to super().process() via provided_attrs. Container flows via
ContextVar, leaving app_state free for user-defined state.
"""

from contextvars import ContextVar
from dataclasses import dataclass

import svcs
from svcs_di.injector_helpers import build_resolved_kwargs
from svcs_hopscotch.auto import hopscotch_get_field_infos
from svcs_hopscotch.injectors.hopscotch import HopscotchInjector
from string.templatelib import Template

from tdom.processor import (
    Attribute,
    ComponentObject,
    ComponentProcessor,
    DefaultAppState,
    ProcessContext,
    TemplateProcessor,
    _prep_component_kwargs,
    _resolve_t_attrs,
    get_callable_info,
)

_di_context: ContextVar[svcs.Container | None] = ContextVar("_di_context", default=None)


def _get_implementation(container: svcs.Container, cls: type) -> type:
    """Get the registered implementation for a class, or the original if none found."""
    try:
        get_impl = container.registry.locator.get_implementation  # ty: ignore[unresolved-attribute]
    except AttributeError:
        return cls
    resource = getattr(container, "resource", None)
    location = getattr(container, "location", None)
    impl = get_impl(
        cls,
        resource=type(resource) if resource is not None else None,
        location=location,
    )
    return impl if impl is not None else cls


def needs_dependency_injection(value: object) -> bool:
    """Check if a callable has Inject[T], Resource[T], or Get[T, Attr] fields."""
    if not callable(value):
        return False
    field_infos = hopscotch_get_field_infos(value)
    return any(
        info.is_injectable or info.is_resource or info.operator is not None
        for info in field_infos
    )


@dataclass(frozen=True)
class DIComponentProcessor(ComponentProcessor):
    """Resolves DI fields through Hopscotch; delegates the call to super()."""

    def process(
        self,
        template: Template,
        last_ctx: ProcessContext,
        app_state: DefaultAppState,
        component_callable: object,
        attrs: tuple,
        component_template: Template,
        provided_attrs: tuple[Attribute, ...] = (),
    ) -> tuple[Template, ComponentObject | None]:
        container = _di_context.get()
        if container is None:
            return super().process(
                template,
                last_ctx,
                app_state,
                component_callable,
                attrs,
                component_template,
                provided_attrs,
            )

        # Component-level locator override (Protocol → impl).
        if isinstance(component_callable, type):
            component_callable = _get_implementation(container, component_callable)

        if not needs_dependency_injection(component_callable):
            return super().process(
                template,
                last_ctx,
                app_state,
                component_callable,
                attrs,
                component_template,
                provided_attrs,
            )

        # Phase 1: pre-prep partial kwargs (template attrs + provided + children, no raise).
        callable_info = get_callable_info(component_callable)
        partial_kwargs = _prep_component_kwargs(
            callable_info,
            _resolve_t_attrs(attrs, template.interpolations),
            children=component_template,
            provided_attrs=provided_attrs,
            raise_on_missing=False,
        )

        # Phase 2: full Hopscotch resolution — Get[T, Attr], locator, adapters, defaults.
        injector = HopscotchInjector(container=container)
        field_infos = hopscotch_get_field_infos(component_callable)  # ty: ignore[invalid-argument-type]
        resolved = build_resolved_kwargs(
            field_infos,
            injector._resolve_field_value_sync,
            partial_kwargs,
        )

        # Phase 3: the DI-fill delta — only fields Hopscotch resolved that weren't in kwargs.
        di_fill = tuple(
            (name, value)
            for name, value in resolved.items()
            if name not in partial_kwargs
        )

        # Phase 4: delegate. super().process() captures component_object via factory branch.
        return super().process(
            template,
            last_ctx,
            app_state,
            component_callable,
            attrs,
            component_template,
            di_fill + provided_attrs,
        )


_tp = TemplateProcessor(
    component_processor_api=DIComponentProcessor(),
    slash_void=True,
    uppercase_doctype=True,
)
_default_ctx = ProcessContext()


def html(
    template: Template,
    *,
    container: svcs.Container | None = None,
) -> str:
    """Process a template string into HTML with DI support.

    Threads ``container`` to components that accept it, and resolves
    Inject[T], Resource[T], and Get[T, Attr] fields via HopscotchInjector
    when ``container`` is provided.

    Examples:
        >>> result = html(t"<div>Hello</div>")
    """
    token = _di_context.set(container)
    try:
        return _tp.process(template, _default_ctx, app_state=None)
    finally:
        _di_context.reset(token)
