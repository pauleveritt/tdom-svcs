# Archive

Completed items grouped by phase. All entries have `done` status.

---

## Phase 1: Foundation

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 1 | Minimal tdom Core Hooks — Add optional config/context parameters to tdom's component resolution and implement pluggable hook system for lifecycle. `S` | Upstreamable hooks in tdom core |
| 2 | Basic svcs Container Integration — Create adapter layer bridging tdom's component system with svcs container; implement DefaultInjector. `S` | Container initialization helpers working |

---

## Phase 2: Core DI Functionality

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 3 | Component Discovery and Registration — Reuse @injectable decorator for marking components; package scanning utility discovers decorated components. `M` | Components register in both ComponentNameRegistry and svcs container |
| 4 | Component Lifecycle Middleware System — Implement pluggable middleware hooks for logging, validation, transformation, error handling. `M` | Middleware works with or without svcs/svcs-di |
| 5 | Documentation and Examples — Create comprehensive documentation covering basic DI patterns, advanced scenarios, testing, and migration guides. `L` | Real-world examples for multi-tenancy and feature flags |

---

## Phase 3: Middleware Examples & Services

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 6 | Aria Verifier Example — Middleware example logging warnings about missing alt attributes. `S` | Example matches all patterns of other examples |
| 7 | Path Middleware — Middleware example and docs for path rewriting using component path collection. `L` | Relative path usage explained; emphasis on standard Python path types |
| 8 | Reorganize Docs — Re-arrange README, delete examples/node placeholder, start page about standard Node type value. `S` | New Node type page for Python web ecosystem interoperability |
| 9 | Refactor Services to svcs-di Pattern — Break all services into svcs-di style modules; create `docs/services/` with narrative documentation. `M` | HopscotchRegistry and HopscotchContainer scanning working |

---

## Phase 5: Performance & Developer Experience

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 17 | Registry Introspection Helpers — Create `list_components()` and `list_middlewares()` helper functions for inspecting registered items. `S` | Runtime inspection and debugging of registry state working |

---

## Phase 6: Dependency Modernization

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 18 | Add tdom-svcs to Workspace — Uncomment `tdom-svcs` from root pyproject.toml and resolve resulting dependency graph. `S` | `uv sync`, `uv run pytest`, `uvx ty check` all work |
| 19 | Migrate Processor Off Node-Based API — Rewrite processor so `html()` returns `str`/`Markup` rather than Node tree. `L` | All 49 Node type annotations and usages updated; tests pass |
| 20 | Drop `services/path/` — Remove entire path service directory, tests, and example app. `S` | Verified via migration mapping checklist |

---

## Phase 7: Port to Pluggable Component Processor

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 22 | Cleanup tdom-svcs Against Current Upstream — Drop `ContextArg` type, remove `is_di_container` TypeGuard and `DIContainer` Protocol; update tests. `S` | `just quality` and test suite pass; no behavior changes |
| 23 | Migrate Component Return Types to Template — Update component Protocols to require `__call__(self) -> Template`; migrate production code and all examples. `L` | Components return `t"..."` directly; tests pass |
| 24 | Port tdom-svcs to ian/integrations with `_invoke_component` Hook — Branch ian/integrations locally; apply hook; replace processor with thin subclass. `M` | Upstream PR open concurrently; tdom-svcs simplified |
| 25 | Adopt tdom-svcs as Workspace-Wide Processor — Switch all direct tdom imports to tdom-svcs; verify byte-identical output. `S` | `container=None` path produces identical output |

---

## Phase 8: Resolution Strategy Refactor

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 26 | Track ian/integrations Directly — Replace workspace branch with direct checkout of ian/integrations HEAD. `S` | No upstream patches required for revised architecture |
| 27 | Rewrite tdom-svcs Processor per Option C — Replace _invoke_component-based DIComponentProcessor with four-phase Option C architecture. `M` | `just quality` runs clean; all regression tests pass |
| 28 | Regression Tests for Full Hopscotch Resolution Surface — Add tests covering each Hopscotch feature routed through Option C. `M` | All seven feature scenarios tested (Inject, Resource, Get, Container self-injection, Locator, Protocol override, component capture, Required-DI fallback, fast path) |
| 29 | Type-Checking Improvements for the Rewrite — Parametrize `_get_implementation[T]`; wrap resolver access in typed seam. `S` | `just quality` passes; protocol-satisfaction test added |
| 30 | Cache Field-Info Helpers in svcs-hopscotch and svcs-di — Add @functools.cache with pytest toggle to avoid cross-test pollution. `S` | `@functools.cache` applied; thread-safe for both GIL and free-threaded builds |
| 31 | Themester Worked Example for Get[T, Attr] — Add example with side-by-side `Inject[Settings] + __post_init__` vs. `Get[Settings, "site_title"]`. `S` | Example and docs show recommended pattern |
| 32 | Eliminate `_tp` and `_default_ctx` Module Globals — Construct per `html()` call rather than module level. `S` | Byte-identical output; matches tdom test idioms |
| 33 | Move Container onto `DIComponentProcessor` (Option B) — Add frozen field; replace ContextVar reads with `self.container`. `M` | Tests updated; ContextVar plumbing deleted |
| 34 | Register `TemplateProcessor` Per-Container via `svcs_container` — Define setup function for Hopscotch scanner; refactor `html()` to dispatcher. `M` | Zero module-level mutable state; svcs is single source of truth |

---

## Phase 9: Rebaseline Against Merged tdom Main

PR #118 (`Component Process API Remix`) merged Ian's processor work into tdom main.
The local workspace checkout was on ian/integrations; Phase 9 rebaselines against
merged main (`b2287f1` / `v0.1.15`).

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 37 | Rebaseline tdom-svcs Processor for PR #118 — Move workspace member from ian/integrations to merged tdom main; update to final non-generic processor API. `M` | `just quality && just test` pass in tdom-svcs; themester smoke checks pass; no stale-API references |

Completed 2026-05-04: `tdom-svcs` targets merged tdom main at `b2287f1`; all quality and test checks pass.

---

## Phase 10: Component Decision Evidence

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 38 | P1 Lean Component Resolution Inspection — Add internal helper for component resolution choice only (native tag, Protocol → impl swap, final callable). `S` | Unit tests cover plain and Protocol components; output unchanged |
| 39 | P1 DI Fill Evidence Propagation — Preserve limited per-field source evidence during rendering (template attr, injected dependency, Get, Resource, default). `M` | Evidence exposed in examples without changing output |

Completed 2026-05-05: ComponentResolutionDecision, _inspect_component_resolution(), and _resolve_component_field_fills() now provide lean and rich evidence.

---

## Phase 11: Package-Local Domain Source

tdom-svcs becomes the second consumer of tainie-tools domain authoring work
after svcs-hopscotch, proving reusability across packages with different native concepts.

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 41 | P0 Align With `tainie-tools` Domain Authoring Policy — Wait for policy spec; this roadmap item points at accepted spec; no contradictions. `S` | Policy published; tdom-svcs follows shared policy |
| 42 | P0 Draft tdom-svcs Package-Local Domain Source — Add `docs/domain/index.md`; enable tainie_tools.sphinx; verify docs build. `M` | Docs build; page remains readable; verified facts use symbol paths where possible |
| 43 | P0 Promote Existing Examples And Tests As Witnesses — Use existing examples/tests as first witnesses covering no-container, Inject, Resource, Get, template-override, locator-aware, required-DI fallback. `M` | Each verified rule has at least one checkable witness |
| 44 | P1 Add Package-Local Domain Validation To CI — Configure tdom-svcs through project configuration; keep small test invoking shared validator. `S` | CI validates syntax, target resolution, duplicate ids, verified-link structure |
| 45 | P1 Exercise Domain Inventory Export — Make tdom-svcs second integration target after svcs-hopscotch. `M` | Exported inventory includes concepts, rules, witnesses, provenance, statuses, and resolved target metadata |
| 46 | P2 Revisit Storyville Witnesses Later — Once Storyville's metadata shape is settled, decide on richer witnesses. `S` | Storyville integration builds on generic witness model |
| 47 | P1 Tainie Component Evidence Provider Integration — Promote judge-confidence component packet into package-owned producer. `M` | Tainie native and Pydantic Evals can attach component evidence; provider drift quarantined; output unchanged |

Completed 2026-05-05 through 2026-05-06: Domain source, validation, inventory export, story witnesses, and component evidence provider all integrated.

---

## Phase 12: Documentation Restructure (Partial)

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 49 | P1 Complete Example Bundle Migration — Migrate remaining `docs/examples/**` pages from `literalinclude` anchors to `example-snippet`/`example-source` directives. `M` | `uv run pytest tests/test_examples.py -q` passes; Sphinx `-W` passes; no stale anchors |

Completed 2026-05-06: Basic, Categories, Hopscotch, and Middleware examples migrated.

---

## Phase 13: Tainie DomainSpec Producer Pilot

tdom-svcs serves as a real producer fixture with validated package-local domain,
example, Storyville, and component-evidence artifacts that Tainie can consume.

| ID | Title | Acceptance Signal |
|----|-------|-------------------|
| 52 | P1 DomainSpec Inventory Pilot For Tainie — Tainie reads tdom-svcs inventories as trusted passive evidence without importing Sphinx or producer docs. `M` | Metrics distinguish domain, example, Storyville, component provider, and compiled evidence; tdom-svcs remains authored source of truth |
| 53 | P1 Split Basic tdom Component Facts From tdom-svcs Service Facts — Make producer-side distinction explicit for future pack generation. `M` | Docs distinguish basic tdom facts from service-aware facts; example review identifies witness curations |

Completed 2026-05-09 and 2026-05-10: Inventories integrated; domain facts split between basic and service-aware concepts.
