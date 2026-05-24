# Backlog

Deferred work items grouped by priority and sequencing constraint.

---

## Phase 10: Component Decision Evidence

After Phase 9 rebaselines the processor against merged `tstring-html`, tdom-svcs
should expose component-rendering decisions in the same style as Hopscotch
resolution evidence.

| ID | Title | Priority | Status | Notes |
|----|-------|----------|--------|-------|
| **TS-40** | P2 TypeForm and Sentinel Deferral — Keep component typing on supported `ty` surface (`TypeIs`, `Literal`, `TypedDict`, `ReadOnly`, `ParamSpec`) and avoid public `TypeForm` or typed `Sentinel` APIs until Tainie's conformance watch says they pass. Acceptance: docs name the gate and link to current probe results. `S` | P2 | Future | Awaits Tainie gate |

---

## Phase 12: Documentation Restructure

| ID | Title | Priority | Status | Notes |
|----|-------|----------|--------|-------|
| **TS-50** | P2 Apply Shared Docs Outline — Restructure published docs navigation after example migration. Expose concise "Why tdom-svcs?" entry point, Concepts/Guides/Reference/Domain/Development sections match shared workspace outline. Acceptance: redirects/links preserve high-value pages, Sphinx `-W` passes. `M` | P2 | Future | After example migration |
| **TS-51** | P2 Shared Example Policy Alignment Audit — After Themester finishes example prep-inventory policy, audit tdom-svcs example bundle migration. Confirm suitable getting-started example set, canonical bundles use stable concept-oriented IDs, multi-file examples use `app.py` + `example.toml`. Acceptance: audit records rationale or focused follow-up; existing tests remain green. `S` | P2 | Future | Depends Themester phase |

---

## Hygiene and Optional Upstream

| ID | Title | Priority | Status | Notes |
|----|-------|----------|--------|-------|
| **TS-B1** | Hygiene fixes from 2026-05-08 deep-dive audit — (a) `tests/test_html_wrapper.py:9` bare `tdom` import violating workspace rule; (b) Public surfaces use `registry: Any` extensively (typing-debt note); (c) End-to-end Tainie component evidence exercise. Acceptance: import fix or documented exception; typing-debt filed; one Tainie test exercises evidence. `S` | Maintenance | Partial | See details |
| **TS-B2** | Optional upstream asks — (1) Drop `_` prefix on `_prep_component_kwargs` and `_resolve_t_attrs` in tdom/processor.py (flags added explicitly to support DI subclasses). (2) Bundle as `ComponentProcessor.prep_partial_kwargs()` static helper for DI subclasses. Both are nice-to-have; tdom-svcs ships fine without them. `S` | Optional | Future | Upstream decision required |

---

## Historical Reference

**2026-05-09 completion note on TS-B1(c):** Tainie now exercises `inspect_component_evidence_packet()` 
against a live `HopscotchContainer` through the registered `component_provider` path, so the component 
evidence contract is pinned end-to-end.

**2026-05-05 fixed:** Stale `register_component` docs (renamed to `register_hookable`). Retired stale 
storyville pytest plugin breakage note (no longer requires `-p no:storyville` workaround).
