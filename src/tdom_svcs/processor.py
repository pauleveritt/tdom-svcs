"""Dependency injection processor for tdom templates.

Resolves DI fields through Hopscotch's full pipeline, then delegates to
super().process() via provided_attrs. The container is carried as a field on
DIComponentProcessor — svcs is the source of truth, no ContextVar.

TemplateProcessor lifecycle: constructed lazily on the first html() call for a
given container and stored as a local value so subsequent calls reuse it.
"""

from dataclasses import dataclass
from string.templatelib import Template
from typing import Literal

import svcs
import tdom
from svcs_di.injector_helpers import FieldResolverWithKwargs, build_resolved_kwargs
from svcs_di.types import FieldInfo, KwargsDict
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


type ComponentResolutionKind = Literal["native-tag", "component"]
type ComponentEvidenceStatus = Literal[
    "selected",
    "no-container",
    "requires-di-container",
]
type ComponentEvidenceBlocker = Literal["container_required"]
type ComponentFieldSource = Literal[
    "template-attr",
    "injected-dependency",
    "field-operator",
    "resource",
    "default",
]


@dataclass(frozen=True, slots=True)
class ComponentResolutionDecision:
    """Lean description of which callable, if any, rendering will use."""

    kind: ComponentResolutionKind
    requested: object
    final_callable: object | None
    implementation_swapped: bool = False


@dataclass(frozen=True, slots=True)
class ComponentFieldEvidence:
    """Evidence for one resolved component field."""

    name: str
    source: ComponentFieldSource
    value: object


@dataclass(frozen=True, slots=True)
class ComponentFieldResolution:
    """Resolved component kwargs plus lean per-field source evidence."""

    kwargs: KwargsDict
    evidence: tuple[ComponentFieldEvidence, ...]


@dataclass(frozen=True, slots=True)
class ComponentFieldEvidencePacket:
    """Serializable evidence for one component field source."""

    name: str
    source: ComponentFieldSource


@dataclass(frozen=True, slots=True)
class ComponentEvidencePacket:
    """Compact component evidence packet for downstream judge fixtures."""

    schema_version: Literal["tdom-svcs.component-evidence.v1"]
    source: Literal["tdom-svcs.processor"]
    status: ComponentEvidenceStatus
    requested_component: str
    selected_component: str | None
    implementation_swapped: bool
    field_evidence: tuple[ComponentFieldEvidencePacket, ...]
    blocker: ComponentEvidenceBlocker | None = None


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


def _inspect_component_resolution(
    container: svcs.Container | None,
    candidate: object,
) -> ComponentResolutionDecision:
    """Inspect native-tag vs component choice and any implementation swap."""
    if isinstance(candidate, str):
        return ComponentResolutionDecision(
            kind="native-tag",
            requested=candidate,
            final_callable=None,
        )

    final_callable = candidate
    if container is not None and isinstance(candidate, type):
        final_callable = _get_implementation(container, candidate)

    return ComponentResolutionDecision(
        kind="component",
        requested=candidate,
        final_callable=final_callable,
        implementation_swapped=final_callable is not candidate,
    )


def _component_label(value: object) -> str:
    module = getattr(value, "__module__", None)
    name = getattr(value, "__qualname__", None)
    if isinstance(module, str) and isinstance(name, str):
        return f"{module}.{name}"
    return repr(value)


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


def _component_field_source(
    field_info: FieldInfo,
    partial_kwargs: KwargsDict,
) -> ComponentFieldSource:
    if field_info.name in partial_kwargs:
        return "template-attr"
    if field_info.operator is not None:
        return "field-operator"
    if field_info.is_resource:
        return "resource"
    if field_info.is_injectable:
        return "injected-dependency"
    return "default"


def _resolve_component_field_fills(
    container: svcs.Container,
    component_callable: object,
    partial_kwargs: KwargsDict,
) -> ComponentFieldResolution:
    """Resolve component fields and preserve lean source evidence."""
    field_infos = hopscotch_get_field_infos(component_callable)  # ty: ignore[invalid-argument-type]
    resolved_kwargs = build_resolved_kwargs(
        field_infos,
        _make_resolver(container),
        partial_kwargs,
    )
    evidence = tuple(
        ComponentFieldEvidence(
            name=field_info.name,
            source=_component_field_source(field_info, partial_kwargs),
            value=resolved_kwargs[field_info.name],
        )
        for field_info in field_infos
        if field_info.name in resolved_kwargs
    )
    return ComponentFieldResolution(kwargs=resolved_kwargs, evidence=evidence)


def _inspect_component_evidence_packet(
    container: svcs.Container | None,
    component_callable: object,
    partial_kwargs: KwargsDict,
) -> ComponentEvidencePacket:
    """Build a compact component decision and field-fill evidence packet."""
    decision = _inspect_component_resolution(container, component_callable)
    requested_component = _component_label(decision.requested)

    if container is None:
        if needs_dependency_injection(component_callable):
            return ComponentEvidencePacket(
                schema_version="tdom-svcs.component-evidence.v1",
                source="tdom-svcs.processor",
                status="requires-di-container",
                requested_component=requested_component,
                selected_component=None,
                implementation_swapped=False,
                field_evidence=(),
                blocker="container_required",
            )
        return ComponentEvidencePacket(
            schema_version="tdom-svcs.component-evidence.v1",
            source="tdom-svcs.processor",
            status="no-container",
            requested_component=requested_component,
            selected_component=_component_label(component_callable),
            implementation_swapped=False,
            field_evidence=(),
        )

    selected_component = (
        _component_label(decision.final_callable)
        if decision.final_callable is not None
        else None
    )
    field_evidence: tuple[ComponentFieldEvidencePacket, ...] = ()
    if decision.final_callable is not None and needs_dependency_injection(
        decision.final_callable
    ):
        field_resolution = _resolve_component_field_fills(
            container,
            decision.final_callable,
            partial_kwargs,
        )
        field_evidence = tuple(
            ComponentFieldEvidencePacket(name=item.name, source=item.source)
            for item in field_resolution.evidence
        )

    return ComponentEvidencePacket(
        schema_version="tdom-svcs.component-evidence.v1",
        source="tdom-svcs.processor",
        status="selected",
        requested_component=requested_component,
        selected_component=selected_component,
        implementation_swapped=decision.implementation_swapped,
        field_evidence=field_evidence,
    )


def inspect_component_evidence_packet(
    container: svcs.Container | None,
    component_callable: object,
    partial_kwargs: KwargsDict,
) -> ComponentEvidencePacket:
    """Build a compact evidence packet for the component renderer path."""
    return _inspect_component_evidence_packet(
        container,
        component_callable,
        partial_kwargs,
    )


def component_evidence_packet_to_mapping(
    packet: ComponentEvidencePacket,
) -> dict[str, object]:
    """Project a detailed tdom-svcs packet into a trusted component report shape."""
    if packet.status == "requires-di-container":
        status = "blocked"
    elif packet.status == "no-container":
        status = "no_container"
    elif packet.status == "selected":
        status = "observed"
    else:
        msg = f"unknown ComponentEvidencePacket.status: {packet.status!r}"
        raise ValueError(msg)
    selected = (
        packet.selected_component if packet.selected_component is not None else "None"
    )
    evidence = [
        f"requested={packet.requested_component}",
        f"selected={selected}",
        f"implementation_swapped={str(packet.implementation_swapped).lower()}",
    ]
    evidence.extend(
        f"field:{field.name}:{field.source}" for field in packet.field_evidence
    )
    if packet.blocker is not None:
        evidence.append(f"blocker={packet.blocker}")

    return {
        "schema_version": "component-evidence.v1",
        "source": packet.source,
        "status": status,
        "component": packet.requested_component,
        "evidence": evidence,
    }


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
        decision = _inspect_component_resolution(container, component_callable)
        if decision.kind == "component" and decision.final_callable is not None:
            component_callable = decision.final_callable

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
        field_resolution = _resolve_component_field_fills(
            container,
            component_callable,
            partial_kwargs,
        )

        # Phase 3: the DI-fill delta: fields Hopscotch resolved that were not in kwargs.
        di_fill = tuple(
            (name, value)
            for name, value in field_resolution.kwargs.items()
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
