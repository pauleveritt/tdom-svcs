# Tainie Component Evidence Provider Design

Date: 2026-05-06

## Summary

Roadmap item 47 should make `tdom-svcs` component evidence consumable by
Tainie through the same evidence-provider architecture that now handles native
route artifacts, optional `svcs-hopscotch` route producers, Pydantic Evals
parity, and live evidence classification.

The recommended shape is a cross-repo provider lane:

- `tdom-svcs` owns the component inspection packet and any package-owned
  conversion helper.
- Tainie owns the trusted evidence provider registry, fixture metadata, provider
  validation, and quarantine behavior.
- The integration is opt-in and import-light: Tainie should not import
  `tdom_svcs` at module import time.

## Context

`tdom-svcs` already exposes `inspect_component_evidence_packet()` as a compact
judge-confidence helper. It can describe selected component overrides,
no-container rendering, required-DI blockers, implementation swaps, and
field-source labels. The packet schema is currently
`tdom-svcs.component-evidence.v1`.

Tainie already has a native evidence provider registry in
`tainie.eval.evidence_providers`. Its route path supports:

- fixture-level opt-in through `route_artifact` or `route_provider`;
- producer registration without top-level downstream imports;
- mapping, projection-object, and native object conversion;
- strict Pydantic validation of trusted evidence packets;
- provider-failure quarantine as provider drift.

Tainie also already has a small trusted component evidence report model:

```python
class ComponentEvidenceReport(BaseModel):
    schema_version: Literal["component-evidence.v1"]
    source: str
    status: Literal["observed", "missing", "blocked"]
    component: str
    evidence: list[str]
```

The missing piece is the bridge between these two shapes.

## Considered Approaches

### 1. Dedicated component provider lane

Add component evidence as a peer to route evidence:

- `component_provider: str | None` fixture metadata in Tainie;
- a `ComponentEvidenceProducer` registry parallel to
  `HOPSCOTCH_ROUTE_PRODUCERS`;
- a default provider factory that asks the registered producer for component
  evidence when the fixture opts in;
- an adapter from `tdom-svcs` packet shape to Tainie's
  `ComponentEvidenceReport`.

This is the recommended approach. It mirrors the route-provider contract while
keeping route semantics and component semantics separate.

### 2. Generic evidence producer registry

Replace the route-specific producer registry with a generalized evidence
producer registry keyed by schema or provider name.

This would reduce future duplication, but it is too much churn for item 47. The
route-provider path has just landed and is useful as a stable pattern.

### 3. Artifact-only handoff

Have `tdom-svcs` write a component evidence artifact and have Tainie load it by
path, similar to `route_artifact`.

This avoids cross-package runtime registration, but it does not prove the
producer-provider contract Tainie has been building. It also makes Pydantic
parity and live provider classification less representative.

## Recommended Design

Use a dedicated component provider lane.

Tainie should add fixture metadata:

```toml
component_provider = "tdom-svcs"
```

The field is independent from `route_provider` so a fixture can request route
evidence, component evidence, both, or neither.

Tainie should add provider types and a registry:

```python
type ComponentEvidenceProducer = Callable[[EvalFixture, Path], object | None]

TDOM_SVCS_COMPONENT_PRODUCERS: dict[str, ComponentEvidenceProducer] = {}
```

The exact dictionary name can follow Tainie's local naming preference, but the
behavior should parallel `HOPSCOTCH_ROUTE_PRODUCERS`.

Tainie should add a default provider factory:

```python
def component_evidence_provider_for(fixture: EvalFixture) -> EvidenceProvider | None:
    producer_name = fixture.component_provider
    if producer_name is None:
        return None
    producer = COMPONENT_EVIDENCE_PRODUCERS.get(producer_name)
    if producer is None:
        return None

    def provider(fixture: EvalFixture, workspace: Path) -> list[TrustedEvidencePacket]:
        projection = producer(fixture, workspace)
        if projection is None:
            return []
        report = component_projection_to_report(projection)
        return [report]

    return provider
```

The default evidence registry should include this factory after the existing
route factories. That makes native and Pydantic Evals entrypoints inherit the
same component evidence path.

## Producer Registration

Tainie should provide a registration helper with the same import discipline as
`register_svcs_hopscotch_route_producer()`:

```python
def register_tdom_svcs_component_producer(
    producer: ComponentEvidenceProducer,
    *,
    name: str = "tdom-svcs",
    import_module: Callable[[str], object] = import_module_object,
) -> bool:
    try:
        import_module("tdom_svcs")
    except ModuleNotFoundError as exc:
        if exc.name == "tdom_svcs":
            return False
        raise
    COMPONENT_EVIDENCE_PRODUCERS[name] = producer
    return True
```

This confirms the package is present only when the caller opts into registering
the producer. A plain Tainie import should not import `tdom_svcs`.

## Projection Contract

The component provider should accept multiple producer return shapes:

- `None`, meaning no trusted evidence for this fixture;
- a mapping that already validates as `ComponentEvidenceReport`;
- an object with `as_component_evidence_v1() -> Mapping[str, object]`;
- a `tdom-svcs` component evidence packet or packet-shaped mapping that can be
  adapted into a Tainie `ComponentEvidenceReport`.

The adapter should be strict. Malformed mappings, inconsistent packet fields, or
unknown statuses should raise through the provider path so Tainie records
provider drift instead of silently trusting bad evidence.

## Packet Mapping

`tdom-svcs` should keep owning the detailed packet:

- `schema_version = "tdom-svcs.component-evidence.v1"`;
- `source = "tdom-svcs.processor"`;
- `status` in `selected`, `no-container`, `requires-di-container`;
- requested component;
- selected component;
- implementation swap flag;
- field evidence;
- optional blocker.

Tainie should map that packet into its trusted report shape:

| tdom-svcs status | Tainie status | Meaning |
| --- | --- | --- |
| `selected` | `observed` | Container-backed component resolution was inspected. |
| `no-container` | `observed` | Plain component rendering path was inspected. |
| `requires-di-container` | `blocked` | Component requires DI and no container was available. |

The report `component` should use the requested component name. The report
`source` should remain `tdom-svcs.processor` unless a producer intentionally
sets a more specific source.

The report `evidence` list should be compact and deterministic:

- `requested=<qualified-name>`;
- `selected=<qualified-name>` or `selected=None`;
- `implementation_swapped=true|false`;
- `field:<name>:<source>`;
- `blocker=container_required` when present.

This keeps Tainie's trusted packet intentionally small while preserving the
judge-confidence facts needed for classification and counting.

## tdom-svcs Ownership

`tdom-svcs` should not grow a dependency on Tainie.

Its package-owned work should be limited to one of these small surfaces:

- add `ComponentEvidencePacket.as_component_evidence_v1()`; or
- add `component_evidence_packet_to_mapping(packet)`.

The helper should return a mapping that Tainie can validate as
`ComponentEvidenceReport`. This makes the package-owned producer easy to write
without making `tdom-svcs` know about Tainie internals.

The existing `inspect_component_evidence_packet()` behavior should remain
unchanged and rendered output must remain unchanged.

## Tests

In `tdom-svcs`:

- keep the current judge-confidence tests for selected override, no-container
  component, required-DI blocker, nested component names, and serializability;
- add coverage for whichever mapping helper is chosen;
- confirm field-source labels remain deterministic.

In Tainie:

- fixture metadata accepts and resolves `component_provider`;
- the default provider registry composes component providers with route
  providers;
- native eval entrypoints attach trusted component evidence for selected,
  no-container, blocked, and field-source cases;
- Pydantic Evals adapter gets the same component evidence counts;
- missing registered producer returns zero evidence rather than failing;
- malformed producer output is quarantined as provider drift;
- importing Tainie modules does not import `tdom_svcs` unless the caller opts
  into the registration helper.

## Scope

In scope:

- small `tdom-svcs` mapping/projection helper;
- Tainie fixture metadata addition;
- Tainie component producer registry and registration helper;
- Tainie adapter from `tdom-svcs` packet shape to trusted component report;
- native and Pydantic tests proving trusted component evidence.

Out of scope:

- automatic discovery of arbitrary component callables from fixture TOML;
- a broad generic evidence producer registry;
- changing Tainie's route-provider behavior;
- changing `tdom-svcs` rendering semantics;
- requiring Tainie to depend on or import `tdom_svcs` by default.

## Implementation Notes

The first implementation plan should split the work into two packages:

1. `tdom-svcs`: expose the mapping/projection helper and tests.
2. Tainie: add the component provider lane and parity tests.

The tests should use deterministic fake producers for Tainie provider behavior.
The real package-owned producer can then be a thin adapter around
`inspect_component_evidence_packet()` rather than a fixture-language design.
