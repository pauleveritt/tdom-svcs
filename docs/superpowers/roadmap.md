# Active Roadmap

## Status Key

- `next` — Ready to start, no blockers
- `blocked` — Waiting on upstream or dependency completion
- `done` — Completed and verified

See `docs/superpowers/roadmap-standards.md` for full conventions, and `docs/superpowers/policies/roadmap-partitioning.md` for the file organization policy.

---

## Phase 8: Resolution Strategy Refactor

After today's upstream activity in `tstring-html` `ian/integrations` (`a877d46`,
`9a5c37c`, `6fb4227`), the supported subclassing surface for DI changed from
"override `_invoke_component`" to "use `_prep_component_kwargs` flags + reordered
merge". This phase re-rewrites tdom-svcs's processor against the new surface,
moves the container from `app_state` to a ContextVar, and locks in `Get[T, Attr]`
and the rest of Hopscotch's resolution pipeline via regression tests.

Phase 8 cleanup items are pending after the processor rewrite completed in the
full roadmap.

| ID | Title | Status | Notes |
|----|-------|--------|-------|
| **TS-35** | Workspace Member Audit and Verification — themester, tdom-layout, storyville imports; byte-identical output verification; grep for stale references. `S` | `next` | → TS-36 |
| **TS-36** | Documentation Refresh for the svcs-as-Source-of-Truth Architecture — update core_concepts, getting_started, research docs, CLAUDE.md, processor docstring; add svcs_container_setup example. `S` | `next` | After TS-35 |

---

## Phase 12: Documentation Restructure

Align tdom-svcs docs to the shared workspace outline while preserving the existing
strong guide, examples, services, and domain material. Add or sharpen "Why tdom-svcs?"
around plain `html()` first and optional container-aware rendering second.

| ID | Title | Status | Notes |
|----|-------|--------|-------|
| **TS-48** | README Overhaul — Rewrite `README.md` against shared README policy. Keep plain `html()` first, optional container-aware rendering second; shorten extended examples; verify docs links and imports. Acceptance: README follows policy, install uses `uv` first, Quick Start is compact. `M` | `next` | — |

---

## Phase 14: Post-Router Coordination

Tainie's 2026-05-13 work landed the domain-router architecture and confirmed that
the three `tdom-svcs.*` packs drive measurable end-to-end wins in model accuracy.
These follow-ups keep tdom-svcs aligned with the router consumer side.

| ID | Title | Status | Notes |
|----|-------|--------|-------|
| **TS-141** | Confirm tdom-svcs pack source-of-truth ownership — The three `tdom-svcs.*` pack files under `tainie/docs/domain/packs/` do not declare `probe_result.source_of_truth` or `compatibility_copy`. Decide explicitly: tdom-svcs-owned (copy into Tainie) or Tainie-owned? Effort: ~0.5d. `S` | `next` | — |
| **TS-142** | Preserve `applies_when` mechanizability for tdom-svcs packs — Add authoring note: `applies_when` entries should remain mechanizable (concrete AST features, field names, import names, method names), not high-level prose. Effort: ~0.5d. `S` | `next` | — |
| **TS-143** | Schema slimming coordination (conditional on Tainie D-3 + 14.1) — If tdom-svcs packs are tdom-svcs-owned (per TS-141), migrate six unused fields (`principles`, `facts`, `probe_result`, `source_decisions`, `compiled_by`, `version`). Effort: ~0.5d. `S` | `blocked` | Awaits TS-141 + Tainie D-3 |
