# Plan: Reduce Middleware to tdom-Specific Concerns

## Context

svcs-di recently added a middleware system (commit `8e2bc03`) that was ported from tdom-svcs. The generic middleware machinery — decorators, protocols, registration, execution pipeline — now lives in svcs-di. tdom-svcs currently duplicates all of this. This refactoring removes the duplicated code from tdom-svcs, keeping only tdom-specific middleware integration (path collection, aria checking, Node tree operations).

Breaking changes are expected — this is an experimental project that prioritizes best design.

## Key Decisions

- **Use svcs-di names directly**: `hookable` (not `component`), `execute_target_middleware` (not `execute_component_middleware`), `"hookable"` category (not `"component"`)
- **Re-export from tdom-svcs**: Users can import middleware symbols from either `tdom_svcs` or `svcs_di`
- **Slim test subset**: Keep ~5-8 integration smoke tests for categories, delete the rest

## Task 1: Save Spec Documentation

Create `agent-os/specs/2026-02-15-reduce-middleware-tdom-specific/` with:
- `plan.md` — This plan
- `shape.md` — Shaping notes from our conversation
- `standards.md` — agent-verification, testing/function-based-tests, testing/fakes-over-mocks
- `references.md` — Pointers to svcs-di middleware and tdom-svcs middleware studied

## Task 2: Delete Duplicate Source Files

### Delete entirely:
- `src/tdom_svcs/middleware.py` — entire file (duplicates `svcs_di.middleware`)
- `src/tdom_svcs/services/middleware/` — entire directory (`__init__.py`, `decorators.py`)

### Strip down `src/tdom_svcs/types.py`:
**Remove** (now in svcs-di):
- `MIDDLEWARE_CATEGORY`, `COMPONENT_CATEGORY` constants
- `Component`, `Props`, `PropsResult`, `MiddlewareResult`, `MiddlewareMap`, `AnyMiddleware` type aliases
- `Context`, `Middleware`, `AsyncMiddleware` protocols

**Keep** (tdom-specific):
- `COMPONENT_LOCATION_PROP` constant
- `DIContainer` protocol + `is_di_container()` function

### Rewrite `src/tdom_svcs/services/__init__.py`:
Strip to only export path-related items (PathCollector, PathMiddleware, etc.) since middleware subpackage is deleted.

## Task 3: Update `__init__.py` Exports

Rewrite `src/tdom_svcs/__init__.py` to:
- **Re-export from svcs-di**: `middleware`, `hookable`, `Middleware`, `AsyncMiddleware`, `execute_middleware`, `execute_middleware_async`, `execute_target_middleware`, `register_middleware`, `register_hookable`
- **Keep local exports**: `html`, `scan`, `ComponentInfo`, `ComponentVariation`, `MiddlewareInfo`, `list_components`, `list_middlewares`
- **Remove**: `component`, `execute_component_middleware`, `Component`

## Task 4: Update Surviving Source Files

### `src/tdom_svcs/introspection.py`:
- Change `from tdom_svcs.middleware import get_middleware_types` → `from svcs_di.middleware import get_middleware_types`
- Change `from tdom_svcs.types import AnyMiddleware` → `from svcs_di.middleware import AnyMiddleware`

### `src/tdom_svcs/scanning.py`:
- Verify it just wraps `svcs_di.scan()` — likely no changes needed

### `src/tdom_svcs/processor.py`:
- Uses `from tdom_svcs.types import is_di_container` — still valid, no changes needed

## Task 5: Delete Duplicate Tests

### Delete entirely:
- `tests/services/middleware/test_middleware_manager.py`
- `tests/services/middleware/test_hook_integration.py`
- `tests/services/middleware/test_integration_end_to_end.py`
- `tests/services/middleware/__init__.py`
- `tests/test_component_middleware_storage.py`

### Check if `tests/services/__init__.py` becomes orphaned (if only middleware/ was under services/). If so, delete `tests/services/` entirely.

## Task 6: Update Surviving Tests

### `tests/test_categories.py` — Reduce to slim integration subset (~5-8 tests):
Keep tests that verify:
- `@middleware` re-export sets category metadata
- `@middleware(categories=[...])` merges additional categories
- `@hookable` re-export sets `"hookable"` category and middleware attr
- `scan()` discovers middleware and hookable items
- `list_middlewares()` introspection works through re-exports
- Imperative `register_middleware()` with categories

Update all imports: `component` → `hookable`, `register_component` → `register_hookable`, `COMPONENT_MIDDLEWARE_ATTR` → `HOOKABLE_MIDDLEWARE_ATTR`, `"component"` category → `"hookable"`.

### `tests/test_free_threading.py`:
- Update type imports: `from tdom_svcs.types import Component, Context, Props, PropsResult` → import from `svcs_di.middleware` (`Target`, `Props`, `PropsResult`) and use `Any` for context

### Other test files:
- `tests/test_context_config_passing.py` — uses `is_di_container`, still valid
- `tests/test_di_injection.py` — verify no middleware imports
- `tests/test_html_wrapper.py` — verify no middleware imports

## Task 7: Delete Generic Examples, Update tdom-Specific Ones

### Delete entirely (generic middleware, no tdom dependency):
- `examples/middleware/basic/`
- `examples/middleware/dependencies/`
- `examples/middleware/scoping/`
- `examples/middleware/error_handling/`

### Update `examples/middleware/aria/`:
- `components.py`: `from tdom_svcs import component` → `from tdom_svcs import hookable`; `@component(middleware=...)` → `@hookable(middleware=...)`
- `middleware.py`: `from tdom_svcs.types import Component, Context, Props, PropsResult` → `from svcs_di.middleware import Target, Props, PropsResult` + `from typing import Any` for context
- `app.py`: `from tdom_svcs import execute_component_middleware` → `from tdom_svcs import execute_target_middleware`; update calls accordingly

### Update `examples/categories/categories_example.py`:
- `component` → `hookable`, `register_component` → `register_hookable`
- `"component"` category → `"hookable"`
- Update import paths

### Verify `examples/middleware/path/` — likely no changes needed (doesn't import from deleted modules)

## Task 8: Update Documentation

### Rewrite `docs/services/middleware.md` (~60-80 lines):
- Explain generic middleware now lives in svcs-di
- Show imports from tdom-svcs (re-exports)
- Focus on tdom-specific use cases: Node tree inspection, path rewriting, accessibility
- Link to svcs-di docs for full middleware reference
- Link to aria and path examples

### Update `docs/examples/middleware/index.md`:
- Remove entries for deleted examples (basic, dependencies, error_handling, scoping)
- Keep aria and path entries
- Update toctree

### Delete example docs:
- `docs/examples/middleware/basic_middleware.md`
- `docs/examples/middleware/dependencies.md`
- `docs/examples/middleware/error_handling.md`
- `docs/examples/middleware/scoping.md`

### Update `docs/services/index.md`:
- Update middleware references to note they come from svcs-di

### Update `docs/categories.md`:
- `@component` → `@hookable`, `register_component` → `register_hookable`
- `"component"` category → `"hookable"`

### Update `docs/how_it_works.md`:
- Rewrite "Middleware System" section to reference svcs-di

### Update `README.md`:
- Simplify middleware section, note it's powered by svcs-di
- Update example code to use `hookable`/`execute_target_middleware`
- Remove references to deleted examples

## Task 9: Verification

1. Use `astral:ruff` skill to check and fix linting
2. Run `uv run pytest tests/ examples/` to verify all tests pass
3. Use `astral:ty` skill to check types
4. Verify no remaining imports from deleted modules: grep for `from tdom_svcs.middleware import`, `from tdom_svcs.services.middleware`, `COMPONENT_MIDDLEWARE_ATTR`, `execute_component_middleware`, `register_component`

## Critical Files Summary

| File | Action |
|------|--------|
| `src/tdom_svcs/middleware.py` | DELETE |
| `src/tdom_svcs/services/middleware/` | DELETE (directory) |
| `src/tdom_svcs/types.py` | STRIP DOWN |
| `src/tdom_svcs/__init__.py` | REWRITE |
| `src/tdom_svcs/introspection.py` | UPDATE imports |
| `src/tdom_svcs/services/__init__.py` | REWRITE |
| `tests/services/middleware/` | DELETE (directory) |
| `tests/test_component_middleware_storage.py` | DELETE |
| `tests/test_categories.py` | REDUCE + UPDATE |
| `tests/test_free_threading.py` | UPDATE imports |
| `examples/middleware/basic/` | DELETE |
| `examples/middleware/dependencies/` | DELETE |
| `examples/middleware/scoping/` | DELETE |
| `examples/middleware/error_handling/` | DELETE |
| `examples/middleware/aria/` | UPDATE |
| `examples/categories/categories_example.py` | UPDATE |
| `docs/services/middleware.md` | REWRITE |
| `docs/examples/middleware/index.md` | UPDATE |
| `docs/examples/middleware/*.md` (4 files) | DELETE |
| `docs/categories.md` | UPDATE |
| `docs/how_it_works.md` | UPDATE |
| `docs/services/index.md` | UPDATE |
| `README.md` | UPDATE |
