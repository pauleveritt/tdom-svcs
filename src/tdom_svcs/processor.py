"""Dependency injection processor for tdom templates.

Resolves DI fields through Hopscotch's full pipeline, then delegates to
super().process() via provided_attrs. The container is carried as a field on
DIComponentProcessor — svcs is the source of truth, no ContextVar.

TemplateProcessor lifecycle: constructed lazily on the first html() call for a
given container and stored as a local value so subsequent calls reuse it.
"""

from dataclasses import dataclass
from string.templatelib import Template

import svcs
import tdom
from svcs_di.injector_helpers import FieldResolverWithKwargs, build_resolved_kwargs
from svcs_hopscotch.auto import hopscotch_get_field_infos
from svcs_hopscotch.injectors.hopscotch import HopscotchInjector
from tdom.parser import TAttribute
from tdom.processor import (
    Attribute,
    ComponentProcessor,
    ProcessContext,
    TemplateProcessor,
    _prep_component_kwargs,
    _resolve_t_attrs,
    get_callable_info,
)


def _get_implementation[T](container: svcs.Container, cls: type[T]) -> type[T]:
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


def _make_resolver(container: svcs.Container) -> FieldResolverWithKwargs:
    """Typed seam for HopscotchInjector._resolve_field_value_sync.

    Passes resource type and location from container so the locator can select
    the correct implementation for Inject[Protocol] fields.
    """
    resource = getattr(container, "resource", None)
    location = getattr(container, "location", None)
    injector = HopscotchInjector(
        container=container,
        resource=type(resource) if resource is not None else None,
        location=location,
    )
    return injector._resolve_field_value_sync


def needs_dependency_injection(value: object) -> bool:
    """Check if callable has ``Inject[T]``, Resource[T], or Get[T, Attr] fields."""
    if not callable(value):
        return False
    field_infos = hopscotch_get_field_infos(value)
    return any(
        info.is_injectable or info.is_resource or info.operator is not None
        for info in field_infos
    )


@dataclass(frozen=True)
class DIComponentProcessor(ComponentProcessor):
    """Resolves DI fields through Hopscotch; delegates the call to super().

    The container is a frozen field rather than a ContextVar: svcs is the
    source of truth, and each processor instance is bound to exactly one
    container at construction time.
    """

    container: svcs.Container | None = None

    def process(
        self,
        template: Template,
        last_ctx: ProcessContext,
        component_callable: object,
        attrs: tuple[TAttribute, ...],
        component_template: Template,
        provided_attrs: tuple[Attribute, ...] = (),
    ) -> Template:
        container = self.container
        if container is None:
            return super().process(
                template,
                last_ctx,
                component_callable,
                attrs,
                component_template,
                provided_attrs,
            )

        # Component-level locator override (Protocol -> impl).
        if isinstance(component_callable, type):
            component_callable = _get_implementation(container, component_callable)

        if not needs_dependency_injection(component_callable):
            return super().process(
                template,
                last_ctx,
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
            raise_on_requires_positional=False,
        )

        # Phase 2: full Hopscotch resolution: Get[T, Attr], locator, adapters, defaults.
        field_infos = hopscotch_get_field_infos(component_callable)  # ty: ignore[invalid-argument-type]
        resolved = build_resolved_kwargs(
            field_infos,
            _make_resolver(container),
            partial_kwargs,
        )

        # Phase 3: the DI-fill delta: fields Hopscotch resolved that were not in kwargs.
        di_fill = tuple(
            (name, value)
            for name, value in resolved.items()
            if name not in partial_kwargs
        )

        # Phase 4: delegate invocation to upstream's component processor.
        return super().process(
            template,
            last_ctx,
            component_callable,
            attrs,
            component_template,
            di_fill + provided_attrs,
        )


def _make_processor(container: svcs.Container) -> TemplateProcessor:
    """Construct a TemplateProcessor pre-wired to the given container."""
    return TemplateProcessor(
        component_processor_api=DIComponentProcessor(container=container),
        slash_void=True,
        uppercase_doctype=True,
    )


def html(
    template: Template,
    *,
    container: svcs.Container | None = None,
) -> str:
    """Process a template string into HTML with DI support.

    When ``container`` is None, delegates to tdom.html() — no DI overhead.

    When ``container`` is provided, resolves a TemplateProcessor from the
    container (lazy-initialising and registering it as a local value on first
    call) so subsequent html() calls on the same container reuse the processor.

    Examples:
        >>> result = html(t"<div>Hello</div>")
    """
    if container is None:
        return tdom.html(template)

    try:
        tp = container.get(TemplateProcessor)
    except svcs.exceptions.ServiceNotFoundError:
        tp = _make_processor(container)
        container.register_local_value(TemplateProcessor, tp)

    return tp.process(template, ProcessContext())
