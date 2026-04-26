# Cleanup Container-Only Context — Shaping Notes

## Scope

Narrow tdom-svcs's public API from accepting any `object | None` to accepting only `svcs.Container | None`.
Remove all type system support for dicts and arbitrary objects (the `DIContainer` Protocol,
`is_di_container` TypeGuard, `ContextArg` type alias). Remove all dead code branches that handled non-container contexts.

This is purely a type and dead-code cleanup with no behavior changes for valid (svcs.Container) callers.

## Decisions

**Encoding container-only design into the type system**: Instead of a broad `object | None` type and a TypeGuard
to distinguish containers from other objects, we now declare `svcs.Container | None` directly. This makes the
intent clear and allows the type checker to enforce it.

**Simplifying type guards**: No need for `is_di_container` since the type system handles it. Plain `context is None`
replaces all `is_di_container(context)` guards.

**Renaming the public parameter**: `context: ContextArg` → `container: svcs.Container | None` makes it clear
to callers that only containers are accepted (not just any context object).

## Context

**Visuals:** None

**References:**
- `docs/research/port-tstring-html-integrations.md` — Stage 1 specification
- `src/tdom_svcs/types.py` — contains deleted types
- `src/tdom_svcs/processor.py` — main implementation file with 8 edits
- `tests/test_context_config_passing.py` — comprehensive context threading tests (5 to update, 4 to delete)

**Product alignment:**
- Phase 6 (Dependency Modernization) item 22 on `agent-os/product/roadmap.md`
- This stage is lowest-risk and recommended first before Stage 2 (Template migration) and Stage 3 (port to ian/integrations)
- Shrinks the fork's dead code before requesting upstream changes

## Standards Applied

- `agent-verification` — Agents verify work using Astral skills (ty, ruff), not justfile
- `testing/function-based-tests` — Tests are functions, never classes (this codebase already follows this)
