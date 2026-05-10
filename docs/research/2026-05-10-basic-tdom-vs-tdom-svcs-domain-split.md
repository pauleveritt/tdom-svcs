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
