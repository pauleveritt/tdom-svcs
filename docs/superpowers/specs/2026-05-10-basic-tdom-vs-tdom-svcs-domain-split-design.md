# Basic tdom vs tdom-svcs Domain Split Design

Date: 2026-05-10

## Goal

Complete roadmap item 53 on the producer side by making the package-local
domain source distinguish basic tdom component facts from service-aware
tdom-svcs facts.

This work should unblock Tainie A-39 conceptually, but it does not regenerate
or promote a generated DomainPack candidate. Candidate rebuild and repeatability
checks remain Tainie-side A-39 work.

## Context

Tainie A-36 repaired the active
`tdom-svcs.canonical-component-shape` pack by keeping the stable pack id while
rewriting the pack body as version `0.2.0` around basic tdom component shape.
The repaired pack intentionally removed service injection, containers,
Hopscotch, Themester verifier conventions, and fixture-specific greeting
details.

tdom-svcs still needs its authored producer evidence to show the same boundary.
Today `docs/domain/index.md` has strong service-aware facts, but the basic
component facts are either implicit or mixed into no-container rendering.

## Scope

In scope:

- Reorganize `docs/domain/index.md` so basic tdom component facts and
  service-aware tdom-svcs facts are named separately.
- Add verified concepts/rules for the basic component facts named by roadmap
  item 53: `Template` returns, callable components, component-tag props,
  default arguments, type hints, and body `children`.
- Retarget or add witnesses from existing examples/tests, preferring boring
  existing sources over new examples.
- Add a short research note recording the A-36 -> item 53 -> A-39 handoff.
- Mark roadmap item 53 complete only after verification passes.

Out of scope:

- Regenerating DomainPack candidates.
- Running Tainie A-39 candidate promotion or repeatability checks.
- Moving pack ownership, changing Tainie active packs, or changing compiler
  manifests.
- Broad Phase 12 docs restructuring.
- Runtime behavior changes.

## Design

### Domain Boundary

`docs/domain/index.md` will keep the current statement that tdom-svcs owns the
integration between t-string HTML rendering and optional service context. It
will add a narrower note for this roadmap item: tdom-svcs is acting as a
producer fixture for basic tdom component evidence because it currently carries
tested examples of those component shapes, not because it owns all core tdom
semantics.

### Basic tdom Component Facts

Add a clearly titled section for basic component facts. The section should
describe:

- A component returns a `string.templatelib.Template` from a t-string literal.
- Components can be ordinary Python callables: functions, dataclasses with
  `__call__`, and plain callable classes.
- Component-tag rendering passes props through t-string component attributes.
- Defaults and type hints remain ordinary Python callable metadata that tdom
  uses when preparing component kwargs.
- Body content is passed as `children: Template` when a component accepts it.

The directives should stay small. Candidate concept ids may include:

- `template-returning-component`
- `callable-component-shape`
- `component-tag-props`
- `component-default-argument`
- `component-type-hint`
- `component-children-template`

Candidate rules may include:

- `basic-components-return-template`
- `component-tags-pass-props`
- `component-body-content-flows-through-children`

### Service-Aware tdom-svcs Facts

Keep the existing DI and Hopscotch material, but group it under a separate
service-aware heading. Existing concepts such as `di-component-processor`,
`injected-component-field`, `resource-context`, `field-operator`, and
`component-implementation-override` should remain verified. The prose should
make clear that these are additive tdom-svcs affordances layered on top of the
basic tdom component model.

### Witnesses

Use existing evidence:

- `examples/basic/pure_tdom.py` for `Template` returns, component-tag props,
  default arguments, and the plain `html()` entry point.
- `examples/basic/function_dataclass_poco.py` for function, dataclass, and
  plain callable class component shapes.
- A small no-container wrapper test for body `children`, so the basic
  component witness stays separate from DI evidence.
- Existing Hopscotch/DI tests for service-aware facts.

The no-container children witness should stay tiny: define a local component
that accepts `children: Template`, render it through plain `html()`, and assert
the body content appears inside the returned template.

### Handoff Note

Add a short research note under `docs/research/` that records:

- A-36 repaired the active pack boundary to v0.2.0 tdom-only content.
- This tdom-svcs item makes the producer-side authored source show the same
  distinction.
- A-39 should rebuild and evaluate the generated candidate from the repaired
  pack after this producer-side split is verified.
- This task intentionally does not claim generated-candidate readiness.

## Verification

Run focused verification after the docs changes:

```bash
uv run pytest tests/test_domain_inventory.py -q
uv run sphinx-build -W -b html docs docs/_build/html
```

If example inventory files or example docs are touched, also run:

```bash
uv run pytest tests/test_examples.py tests/test_example_docs_migration.py -q
```

Before marking the roadmap item complete, re-read the acceptance criteria and
confirm:

- `docs/domain/index.md` distinguishes basic tdom component facts from
  service-aware tdom-svcs facts.
- The example inventory review identifies curated examples for the basic
  component concepts separately from DI examples.
- The roadmap or research note points back to Tainie A-36 and forward to A-39.

## Risks

- The word "tdom" can make ownership look wrong. Mitigation: say explicitly
  that tdom-svcs is producing evidence for current tested examples, while core
  tdom semantics remain upstream-owned.
- Overloading `docs/domain/index.md` with too many directives can make the page
  less readable. Mitigation: use prose first and add only durable concepts,
  rules, and witnesses.
- Children evidence can accidentally drift into service-aware tests.
  Mitigation: keep a dedicated no-container wrapper test as the basic witness.
