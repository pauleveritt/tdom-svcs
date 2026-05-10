# tdom-svcs Domain

This is the package-local domain source for `tdom-svcs`.

It follows the shared `tainie-tools` Domain Authoring Policy. The page is
documentation first: prose explains the rendering boundary, and small
`domain:*` directives mark the first facts that tooling can extract and
validate.

## Boundary

tdom-svcs owns the integration between t-string HTML rendering and optional
service context.

It does not own the core `tdom` parser, the whole Hopscotch selection model, or
application-specific component vocabulary. Those belong in neighboring
packages or in the consuming application. tdom-svcs should prove that the
shared domain authoring model works for a rendering integration package without
inventing a tdom-svcs-only DomainPack format.

The authoring boundary stays simple: `from tdom_svcs import html` remains the
obvious first move. Containers, resource-aware selection, field operators, and
component implementation overrides are additive affordances for larger
component trees.

For the DomainPack producer pipeline, this package also carries verified
evidence for a small set of basic tdom component facts. That does not transfer
ownership of core tdom semantics to tdom-svcs. It means tdom-svcs currently has
the tested examples and inventories that Tainie can use to check the boundary
between ordinary component rendering and service-aware rendering.

## Vocabulary

The vocabulary is intentionally small and split into two groups. Basic tdom
component facts describe the component shapes that exist before dependency
injection. Service-aware tdom-svcs facts describe the optional container,
Hopscotch, and evidence affordances layered on top.

### Basic tdom Component Facts

| Concept | Meaning | Native Symbols |
| --- | --- | --- |
| Template-returning component | A component returns a `Template` produced by a t-string literal. | `string.templatelib.Template` |
| Callable component shape | Components may be functions, dataclasses with `__call__`, or plain callable classes. | Python callables |
| Component-tag props | T-string component attributes become component kwargs. | t-string component attributes |
| Component default argument | Ordinary Python defaults provide component values when props do not. | Python callable defaults |
| Component type hint | Type hints document component props and let the processor prepare kwargs. | Python annotations |
| Component children template | Body content is passed as `children: Template` when accepted by the component. | `string.templatelib.Template` |

### Service-Aware tdom-svcs Facts

| Concept | Meaning | Native Symbols |
| --- | --- | --- |
| Render entry point | Public `html()` wrapper that preserves plain rendering and adds optional container-aware processing. | `tdom_svcs.html` |
| DI component processor | Component processor that resolves Hopscotch fields, then delegates invocation to upstream tdom processing. | `tdom_svcs.processor.DIComponentProcessor` |
| Container context | Optional `svcs.Container` passed to `html()` for request or operation scoped resolution. | `svcs.Container` |
| Injected component field | Component constructor field resolved from the container when not supplied by template attributes. | `svcs_di.Inject` |
| Resource context | Downstream-owned request or operation object carried by the Hopscotch container. | `HopscotchContainer.resource` |
| Resource marker | Annotation marker that asks for the current resource as a specific downstream type. | `svcs_hopscotch.Resource` |
| Field operator | Field-level operator such as `Get[T, Attr]` resolved through Hopscotch. | `svcs_hopscotch.Get` |
| Template attribute override | Explicit template attributes win over injected values. | t-string component attributes |
| Component implementation override | Template names a base component or protocol while Hopscotch selects a registered implementation. | `HopscotchRegistry.register_implementation` |
| Component evidence packet | Compact internal packet that combines component selection and field source evidence for downstream judge fixtures. | `tdom_svcs.processor.ComponentEvidencePacket` |
| No-container rendering | Rendering with `container=None`, delegated to `tdom.html()`. | `tdom_svcs.html` |
| String output testing | Direct string assertions for small or exact rendered output. | `tdom_svcs.html` |
| Structured HTML testing | HTML-aware assertions for structure, roles, names, and accessibility. | `aria-testing` |

## Testing Boundary

tdom-svcs based applications should choose the smallest honest test surface.

For tiny examples, exact rendering contracts, and no-container smoke tests,
string assertions are good evidence. They are easy to read and catch byte-level
changes.

For component structure, accessibility, and user-facing semantics, tests should
query rendered HTML with an HTML-aware tool such as `aria-testing`. Those tests
should ask questions like "is there an image without alt text?" or "does this
role/name exist?" instead of matching a large HTML string.

Dependency-aware tests should use fakes or small registered values in a real
container when the behavior depends on injection, resource context, or
implementation selection.

## Validated Domain Facts

These directives are a small first inventory, not an exhaustive ontology. They
prefer importable symbol references where the fact has a stable symbol and use
existing regression tests as witnesses for behavior.

:::{domain:concept} Template-returning component
:id: template-returning-component
:status: verified
:kind: component
:ref: string.templatelib:Template

A component returns a `Template` produced by a t-string literal, such as
`t"<h1>Hello {name}</h1>"`, so the renderer can continue processing nested
template content.
:::

:::{domain:concept} Callable component shape
:id: callable-component-shape
:status: verified
:kind: component
:ref: tdom.processor:ComponentProcessor

The basic component model accepts ordinary Python callable shapes: functions,
dataclasses with `__call__`, and plain callable classes.
:::

:::{domain:concept} Component-tag props
:id: component-tag-props
:status: verified
:kind: props
:ref: tdom.processor:ComponentProcessor

T-string component attributes, such as `name='Alice'`, are prepared as keyword
arguments for the component callable.
:::

:::{domain:concept} Component default argument
:id: component-default-argument
:status: verified
:kind: props
:ref: tdom.processor:get_callable_info

Ordinary Python default arguments remain part of the component contract when a
template does not provide a prop.
:::

:::{domain:concept} Component type hint
:id: component-type-hint
:status: verified
:kind: props
:ref: tdom.processor:get_callable_info

Component type hints document the expected prop shape and are part of the
callable metadata used while preparing component kwargs.
:::

:::{domain:concept} Component children template
:id: component-children-template
:status: verified
:kind: props
:ref: string.templatelib:Template

When a component accepts `children`, tdom passes body content as a `Template`
that the component can interpolate into its returned template.
:::

:::{domain:concept} Render entry point
:id: render-entry-point
:status: verified
:kind: function
:ref: tdom_svcs:html

The public function authors import to render ordinary templates and, when
needed, pass an optional container for dependency-aware component rendering.
:::

:::{domain:concept} DI component processor
:id: di-component-processor
:status: verified
:kind: class
:ref: tdom_svcs.processor:DIComponentProcessor

The processor that fills dependency-aware component fields through Hopscotch
before delegating component invocation to the upstream tdom processor.
:::

:::{domain:concept} Injected component field
:id: injected-component-field
:status: verified
:kind: field-marker
:ref: svcs_di:Inject

A typed field marker that asks the container to provide a value when the
template does not provide one explicitly.
:::

:::{domain:concept} Resource context
:id: resource-context
:status: verified
:kind: context
:ref: svcs_hopscotch:HopscotchContainer

The current request or operation object carried by a Hopscotch container. Its
shape is downstream-owned: a framework or application may use a protocol,
dataclass, request object, content object, tenant object, or any other resource
type it commits to provide.
:::

:::{domain:concept} Resource marker
:id: resource-marker
:status: verified
:kind: field-marker
:ref: svcs_hopscotch:Resource

The `Resource[T]` annotation marker that asks Hopscotch for the current
resource and lets the component describe the downstream resource shape it
expects.
:::

:::{domain:concept} Field operator
:id: field-operator
:status: verified
:kind: operator
:ref: svcs_hopscotch:Get

A field-level resolution operator, such as `Get[T, Attr]`, handled by
Hopscotch during component construction.
:::

:::{domain:concept} Component implementation override
:id: component-implementation-override
:status: verified
:kind: selection
:ref: svcs_hopscotch:HopscotchRegistry

A registry-level binding that lets a template name a base component or protocol
while Hopscotch selects a registered implementation for rendering.
:::

:::{domain:concept} Component evidence packet
:id: component-evidence-packet
:status: verified
:kind: evidence
:ref: tdom_svcs.processor:inspect_component_evidence_packet

A compact packet for judge-confidence fixtures. It records the
requested component, selected component, implementation swap flag, field source
labels, and negative no-container or required-DI status without exposing field
values.
:::

:::{domain:concept} String output testing
:id: string-output-testing
:status: verified
:kind: testing
:ref: tdom_svcs:html

Direct assertions against rendered strings. This is appropriate for small
examples, exact wrapper behavior, and byte-level rendering contracts.
:::

:::{domain:concept} Structured HTML testing
:id: structured-html-testing
:status: verified
:kind: testing
:ref: aria_testing:query_all_by_tag_name

HTML-aware testing that queries rendered output by structure, role, accessible
name, or tag rather than matching a large string.
:::

:::{domain:rule} Basic components return Template
:id: basic-components-return-template
:status: verified
:applies-to: template-returning-component, callable-component-shape

The canonical component shape returns `string.templatelib.Template` from a
t-string literal rather than manually constructing rendered HTML strings inside
the component.
:::

:::{domain:rule} Component tags pass props
:id: component-tags-pass-props
:status: verified
:applies-to: component-tag-props, component-default-argument, component-type-hint

Component-tag attributes are caller-provided props. They override callable
defaults, while omitted props can still fall back to ordinary Python default
arguments.
:::

:::{domain:rule} Component body content flows through children
:id: component-body-content-flows-through-children
:status: verified
:applies-to: component-children-template

Body content written between opening and closing component tags is passed to a
component as `children` when the callable accepts that parameter.
:::

:::{domain:rule} No-container rendering stays plain
:id: no-container-rendering-stays-plain
:status: verified
:applies-to: render-entry-point

Calling `html(template)` without a container delegates to `tdom.html()` and
does not require registry or container setup.
:::

:::{domain:rule} Template attributes override injection
:id: template-attributes-override-injection
:status: verified
:applies-to: injected-component-field, field-operator

Explicit t-string component attributes are treated as caller-provided props and
win over values that Hopscotch could otherwise resolve from the container.
:::

:::{domain:rule} Component DI flows through Hopscotch
:id: component-di-flows-through-hopscotch
:status: verified
:applies-to: di-component-processor, injected-component-field, resource-context, resource-marker, field-operator, component-implementation-override

When a container is supplied, dependency-aware component fields are resolved
through Hopscotch's field-resolution path before tdom invokes the component.
:::

:::{domain:rule} Resource shape is downstream-owned
:id: resource-shape-is-downstream-owned
:status: verified
:applies-to: resource-context, resource-marker

tdom-svcs and Hopscotch do not define the members of a resource. They define
the transport and marker: downstream frameworks or applications provide the
resource instance on the container and use `Resource[T]` to state the expected
shape of that instance.
:::

:::{domain:rule} Tests match output risk
:id: tests-match-output-risk
:status: verified
:applies-to: string-output-testing, structured-html-testing, render-entry-point

Simple rendering behavior may be tested with direct strings. Structural,
semantic, and accessibility behavior should use HTML-aware queries such as
`aria-testing`, with fakes or real containers added when dependency injection
is part of the behavior.
:::

:::{domain:witness} ../../examples/basic/pure_tdom.py
:id: pure-tdom-component-shape-witness
:status: verified
:kind: example
:proves: basic-components-return-template, component-tags-pass-props, no-container-rendering-stays-plain

The pure tdom example defines a function component with a typed prop, a default
argument, a `Template` return value, and a component-tag render call through the
plain `html()` entry point.
:::

:::{domain:witness} ../../examples/basic/function_dataclass_poco.py
:id: component-flavors-witness
:status: verified
:kind: example
:proves: basic-components-return-template, callable-component-shape, component-tags-pass-props

The component flavors example shows the same component-tag props pattern across
a function component, a dataclass component with `__call__`, and a plain
callable class.
:::

:::{domain:witness} ../../tests/test_html_wrapper.py
:id: component-children-witness
:status: verified
:kind: test
:proves: component-body-content-flows-through-children, no-container-rendering-stays-plain

This regression test covers a component that accepts `children: Template` and
receives body content through the plain no-container `html()` path.
:::

:::{domain:witness} ../../tests/test_html_wrapper.py
:id: html-wrapper-witness
:status: verified
:kind: test
:proves: no-container-rendering-stays-plain, string-output-testing, tests-match-output-risk

This regression test proves that the public wrapper delegates to `tdom.html()`
when `container=None`.
:::

:::{domain:witness} ../node.md
:id: aria-testing-doc-witness
:status: verified
:kind: docs
:proves: structured-html-testing, tests-match-output-risk

The Node standard page records the intended `aria-testing` pattern for querying
component output by structure instead of matching broad HTML strings.
:::

:::{domain:witness} ../../tests/test_hopscotch_resolution.py
:id: inject-field-witness
:status: verified
:kind: test
:proves: component-di-flows-through-hopscotch, injected-component-field

This regression test covers a component field resolved through `Inject[T]`.
:::

:::{domain:witness} ../../tests/test_hopscotch_resolution.py
:id: resource-field-witness
:status: verified
:kind: test
:proves: component-di-flows-through-hopscotch, resource-context, resource-marker, resource-shape-is-downstream-owned

This regression test covers `Resource[T]` injection from the current container
resource.
:::

:::{domain:witness} ../../tests/test_hopscotch_resolution.py
:id: field-operator-witness
:status: verified
:kind: test
:proves: component-di-flows-through-hopscotch, field-operator

This regression test covers `Get[T, Attr]` operator resolution through
Hopscotch.
:::

:::{domain:witness} ../../tests/test_hopscotch_resolution.py
:id: template-override-witness
:status: verified
:kind: test
:proves: template-attributes-override-injection

This regression test covers explicit template attributes winning over field
operator resolution.
:::

:::{domain:witness} ../../tests/test_hopscotch_resolution.py
:id: component-implementation-override-witness
:status: verified
:kind: test
:proves: component-di-flows-through-hopscotch, component-implementation-override

This regression test covers a template that names a protocol while Hopscotch
selects the registered implementation.
:::

:::{domain:witness} ../../tests/test_judge_confidence_evidence.py
:id: component-evidence-packet-witness
:status: verified
:kind: test
:proves: component-evidence-packet, component-implementation-override, template-attributes-override-injection, component-di-flows-through-hopscotch, no-container-rendering-stays-plain

This regression test covers the compact packet shape Tainie can consume for
selected overrides, field source labels, stable component provenance,
no-container rendering, and missing container evidence for required DI.
:::

:::{domain:witness} ../../tests/test_hopscotch_resolution.py
:id: required-di-field-witness
:status: verified
:kind: test
:proves: component-di-flows-through-hopscotch, injected-component-field

This regression test covers a required injected field with no template
attribute or dataclass default.
:::

:::{domain:witness} examples/basic/pure_tdom.py
:id: pure-tdom-example-witness
:status: verified
:kind: example
:proves: no-container-rendering-stays-plain

The minimal example starts from the public render entry point and uses no
container setup.
:::
