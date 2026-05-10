# Basic tdom vs tdom-svcs Domain Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the tdom-svcs producer-side domain source explicitly separate basic tdom component facts from service-aware tdom-svcs facts.

**Architecture:** This is a docs/source-only change. `docs/domain/index.md` remains the authored source, `tests/test_domain_inventory.py` guards exported domain records, `docs/research/` records the A-36 -> item 53 -> A-39 handoff, and `docs/superpowers/roadmap.md` is marked complete only after verification.

**Tech Stack:** Sphinx, MyST, `tainie_tools.sphinx` domain directives, pytest, uv.

---

## File Structure

- Modify: `tests/test_domain_inventory.py`
  - Responsibility: assert the generated domain inventory contains the new basic-component records and key witness links.
- Modify: `tests/test_html_wrapper.py`
  - Responsibility: prove component `children` flows through the plain no-container `html()` path.
- Modify: `docs/domain/index.md`
  - Responsibility: prose-first domain source with small verified `domain:*` directives.
- Create: `docs/research/2026-05-10-basic-tdom-vs-tdom-svcs-domain-split.md`
  - Responsibility: short handoff note from Tainie A-36 to tdom-svcs item 53 to Tainie A-39.
- Modify: `docs/superpowers/roadmap.md`
  - Responsibility: mark item 53 complete after verification.

Do not commit automatically. Stop with a clean summary and leave review to the user.

## Task 1: Add Domain Inventory Expectations

**Files:**
- Modify: `tests/test_domain_inventory.py`

- [ ] **Step 1: Add the expected basic-domain record ids**

In `tests/test_domain_inventory.py`, extend the set assertion inside
`test_docs_build_validates_and_exports_domain_inventory()` so it includes these
new ids:

```python
        "template-returning-component",
        "callable-component-shape",
        "component-tag-props",
        "component-default-argument",
        "component-type-hint",
        "component-children-template",
        "basic-components-return-template",
        "component-tags-pass-props",
        "component-body-content-flows-through-children",
        "pure-tdom-component-shape-witness",
        "component-flavors-witness",
        "component-children-witness",
```

- [ ] **Step 2: Add focused assertions for the new facts**

Add these assertions after the existing `resource_witness` assertions:

```python
    template_component = records["template-returning-component"]
    assert template_component["fact_kind"] == "concept"
    assert template_component["status"] == "verified"
    assert template_component["target"]["kind"] == "symbol"
    assert template_component["target"]["resolved"] is True

    pure_tdom_witness = records["pure-tdom-component-shape-witness"]
    assert pure_tdom_witness["fact_kind"] == "witness"
    assert pure_tdom_witness["target_reference"]["resolved"] is True
    assert "basic-components-return-template" in pure_tdom_witness["proves"]
    assert "component-tags-pass-props" in pure_tdom_witness["proves"]

    children_witness = records["component-children-witness"]
    assert children_witness["fact_kind"] == "witness"
    assert children_witness["target_reference"]["resolved"] is True
    assert "component-body-content-flows-through-children" in children_witness[
        "proves"
    ]
    assert "no-container-rendering-stays-plain" in children_witness["proves"]
    assert "component-di-flows-through-hopscotch" not in children_witness["proves"]
```

- [ ] **Step 3: Run the focused test and confirm it fails**

Run:

```bash
uv run pytest tests/test_domain_inventory.py -q
```

Expected: FAIL because the new domain records do not exist yet.

## Task 2: Split the Domain Source

**Files:**
- Modify: `docs/domain/index.md`

- [ ] **Step 1: Update the boundary prose**

In the `## Boundary` section, add a paragraph after the existing authoring
boundary paragraph:

```markdown
For the DomainPack producer pipeline, this package also carries verified
evidence for a small set of basic tdom component facts. That does not transfer
ownership of core tdom semantics to tdom-svcs. It means tdom-svcs currently has
the tested examples and inventories that Tainie can use to check the boundary
between ordinary component rendering and service-aware rendering.
```

- [ ] **Step 2: Replace the vocabulary lead-in with two groups**

Change `The initial vocabulary is intentionally small:` to:

```markdown
The vocabulary is intentionally small and split into two groups. Basic tdom
component facts describe the component shapes that exist before dependency
injection. Service-aware tdom-svcs facts describe the optional container,
Hopscotch, and evidence affordances layered on top.

### Basic tdom Component Facts
```

Add this table under `### Basic tdom Component Facts`:

```markdown
| Concept | Meaning | Native Symbols |
| --- | --- | --- |
| Template-returning component | A component returns a `Template` produced by a t-string literal. | `string.templatelib.Template` |
| Callable component shape | Components may be functions, dataclasses with `__call__`, or plain callable classes. | Python callables |
| Component-tag props | T-string component attributes become component kwargs. | t-string component attributes |
| Component default argument | Ordinary Python defaults provide component values when props do not. | Python callable defaults |
| Component type hint | Type hints document component props and let the processor prepare kwargs. | Python annotations |
| Component children template | Body content is passed as `children: Template` when accepted by the component. | `string.templatelib.Template` |
```

Before the existing render-entry-point row, add this heading:

```markdown
### Service-Aware tdom-svcs Facts
```

- [ ] **Step 3: Add basic component concepts before `Render entry point`**

Insert these directives before the existing `Render entry point` concept:

```markdown
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
:ref: examples.basic.function_dataclass_poco:Greeting1

The basic component model accepts ordinary Python callable shapes: functions,
dataclasses with `__call__`, and plain callable classes.
:::

:::{domain:concept} Component-tag props
:id: component-tag-props
:status: verified
:kind: props
:ref: examples.basic.pure_tdom:Greeting

T-string component attributes, such as `name='Alice'`, are prepared as keyword
arguments for the component callable.
:::

:::{domain:concept} Component default argument
:id: component-default-argument
:status: verified
:kind: props
:ref: examples.basic.pure_tdom:Greeting

Ordinary Python default arguments remain part of the component contract when a
template does not provide a prop.
:::

:::{domain:concept} Component type hint
:id: component-type-hint
:status: verified
:kind: props
:ref: examples.basic.pure_tdom:Greeting

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
```

- [ ] **Step 4: Add basic component rules before `No-container rendering stays plain`**

Insert these directives before the existing `No-container rendering stays
plain` rule:

```markdown
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
```

- [ ] **Step 5: Add the basic witnesses**

Insert these witness directives before the existing `html-wrapper-witness`:

```markdown
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
```

- [ ] **Step 6: Run the focused test and confirm it passes**

Run:

```bash
uv run pytest tests/test_domain_inventory.py -q
```

Expected: PASS.

## Task 3: Add the A-36 to A-39 Handoff Note

**Files:**
- Create: `docs/research/2026-05-10-basic-tdom-vs-tdom-svcs-domain-split.md`

- [ ] **Step 1: Create the research note**

Create `docs/research/2026-05-10-basic-tdom-vs-tdom-svcs-domain-split.md`:

```markdown
# Basic tdom vs tdom-svcs Domain Split

Date: 2026-05-10

## Question

What producer-side tdom-svcs work must happen before Tainie A-39 rebuilds and
reconfirms the generated candidate for `tdom-svcs.canonical-component-shape`?

## Decision

tdom-svcs roadmap item 53 is the producer-side prerequisite. The package-local
domain source now separates basic tdom component facts from service-aware
tdom-svcs facts:

- basic tdom component facts: `Template` returns, callable component shapes,
  component-tag props, ordinary defaults, type hints, and body `children`;
- service-aware tdom-svcs facts: optional containers, Hopscotch resolution,
  injected fields, field operators, resource context, implementation overrides,
  and component evidence packets.

This keeps `from tdom_svcs import html` as the first move while making
container-aware rendering an additive affordance.

## A-36 Input

Tainie A-36 repaired the active
`tdom-svcs.canonical-component-shape` pack by keeping the stable pack id and
rewriting the pack body as v0.2.0 around basic tdom component shape. The repair
removed service injection, containers, Hopscotch, Themester verifier
conventions, and fixture-specific greeting details from the canonical component
pack boundary.

## A-39 Handoff

This tdom-svcs work does not regenerate or promote a candidate. It gives A-39 a
clean producer-side source boundary to consume.

Tainie A-39 should rebuild the generated candidate from the repaired v0.2.0
tdom-only pack sources and then run the generated-candidate repeatability gate.
The A-39 research note should explicitly state whether the repaired tdom-only
pack preserves the A-34/A-35 signal.

## Evidence

Producer-side verification should cite:

- `docs/domain/index.md` for the authored split;
- `domain-inventory.json` from the Sphinx build for exported facts;
- `examples/basic/pure_tdom.py` and
  `examples/basic/function_dataclass_poco.py` for basic component witnesses;
- existing Hopscotch and DI tests for service-aware witnesses.
```

- [ ] **Step 2: Build docs with warnings as errors**

There is no `docs/research/index.md` in this repo, and `docs/research/**` is
excluded from Sphinx source discovery. The roadmap completion note is the
durable discovery link for this handoff note.

Run:

```bash
uv run sphinx-build -W -b html docs docs/_build/html
```

Expected: exit code 0.

## Task 4: Complete Roadmap Item 53

**Files:**
- Modify: `docs/superpowers/roadmap.md`

- [ ] **Step 1: Update item 53 checkbox and completion note**

Change item 53 from `[ ]` to `[x]` and add this completion paragraph after the
acceptance paragraph:

```markdown
    Completed 2026-05-10: `docs/domain/index.md` now separates basic tdom
    component facts from service-aware tdom-svcs facts. Basic facts cover
    `Template` returns, callable component shapes, component-tag props, default
    arguments, type hints, and body `children`; service-aware facts remain
    scoped to container-aware rendering, Hopscotch resolution, injected props,
    field operators, resource context, implementation overrides, and component
    evidence packets. The handoff note
    `docs/research/2026-05-10-basic-tdom-vs-tdom-svcs-domain-split.md` records
    the A-36 producer boundary repair and leaves generated-candidate rebuild and
    repeatability confirmation to Tainie A-39.
```

- [ ] **Step 2: Run final verification**

Run:

```bash
uv run pytest tests/test_domain_inventory.py -q
uv run sphinx-build -W -b html docs docs/_build/html
```

Expected: both commands exit 0.

- [ ] **Step 3: Review the diff**

Run:

```bash
git diff -- docs/domain/index.md tests/test_domain_inventory.py docs/research/2026-05-10-basic-tdom-vs-tdom-svcs-domain-split.md docs/superpowers/roadmap.md docs/superpowers/specs/2026-05-10-basic-tdom-vs-tdom-svcs-domain-split-design.md docs/superpowers/plans/2026-05-10-basic-tdom-vs-tdom-svcs-domain-split.md
```

Expected: changes are limited to the approved design, implementation plan,
domain source, domain inventory test, handoff note, and roadmap completion
note.

Do not stage or commit unless the user explicitly asks.
