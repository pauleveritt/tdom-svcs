# Add tdom-svcs to Workspace

## Context

tdom-svcs was commented out of the uv workspace members list at the monorepo root
(`/Users/pauleveritt/projects/t-strings/pyproject.toml`). This blocks Phase 6 of the
roadmap (Dependency Modernization) — items 19 and 20 both depend on tdom-svcs being a
proper workspace member first.

The recent commit `aca7263` did the prep work: converted `[tool.uv.sources]` from
`path = "..." editable = true` to `workspace = true`.

## What Was Actually Done

The work was larger than the `S` sizing suggested because two API migrations had occurred
in sibling packages since tdom-svcs was last in the workspace:

1. **`HopscotchContainer` / `HopscotchRegistry` moved** from `svcs_di.injectors` to
   `svcs_hopscotch.injectors`. Also: `injectable`, `scan`, `KeywordInjector`, middleware
   types, and `HopscotchInjector` all moved to `svcs_hopscotch`. Updated 40 files.

2. **`tdom.nodes` removed** in tstring-html v0.1.15. The old node-object API
   (`Node/Element/Fragment/Text`) no longer exists. `processor.py` was stubbed to
   delegate to `tdom.html()` until item 20 ("Migrate Processor Off the Node-Based API")
   rewrites it properly. `collector.py` node-walker methods also stubbed.

## Tasks Completed

### Task 1: Save Spec Documentation ✓

Created `agent-os/specs/2026-04-11-add-tdom-svcs-to-workspace/` with plan, shape,
standards, and references files.

### Task 2: Uncomment tdom-svcs in workspace root ✓

Edited `/Users/pauleveritt/projects/t-strings/pyproject.toml` to uncomment `tdom-svcs`.

### Task 3: Add svcs-hopscotch dependency and migrate imports ✓

- Added `svcs-hopscotch` to `pyproject.toml` dependencies and `[tool.uv.sources]`
- Updated 40 files: `svcs_di.injectors` → `svcs_hopscotch.injectors`,
  `svcs_di.hopscotch_registry` → `svcs_hopscotch.hopscotch_registry`,
  `svcs_di.middleware` → `svcs_hopscotch.middleware`
- Ran `uv sync` — resolved cleanly

### Task 4: Stub processor.py and collector.py for tstring-html v0.1.15+ ✓

- `processor.py`: Removed all `tdom.nodes` and old `tdom.parser` imports; `html()`
  now delegates to `tdom.html()`. `_get_implementation()` kept (no Node dependency).
- `collector.py`: Removed `Element/Fragment/Node` imports; `collect_from_node()` and
  `_walk_and_collect()` stubbed.
- Updated type annotations across 20+ files: `Node` → `Markup`, `-> Markup:` → `-> str | Markup:`
- Stubbed `AriaVerifierMiddleware._check_images()` (used `query_all_by_tag_name` on
  Node objects — item 20 will restore this).

### Task 5: Verify ✓

| Check | Result |
|-------|--------|
| `uv sync` (workspace root) | Clean |
| `uvx ty check` (subdirectory) | All checks passed |
| `uv run --package tdom-svcs pytest` (workspace root) | 62 pass, 48 fail, 19 skip |
| `uv run pytest` (subdirectory) | 62 pass, 48 fail, 19 skip |

The 48 failures are all DI-in-`html()` tests — requiring item 20's full processor
rewrite for the new `ProcessorService` API.

## Key Files Changed

- `/Users/pauleveritt/projects/t-strings/pyproject.toml` — workspace root (uncommented tdom-svcs)
- `pyproject.toml` — added `svcs-hopscotch` dep and workspace source
- `src/tdom_svcs/processor.py` — stubbed for item 20
- `src/tdom_svcs/services/path/collector.py` — stubbed node-walker for item 20
- 40 source/test/example files — import migration from svcs_di → svcs_hopscotch

## Next: Item 20

Item 19 (rename `tdom` → `tstring-html`) is a mechanical rename.
Item 20 (`L`) rewrites `processor.py` and `collector.py` using the new
`ProcessorService` class-based API, which will un-stub everything and restore the 48
failing tests.
