# Item 23 — Migrate Component Return Types to Template

## Context

After item 22, `tdom-svcs` uses `TemplateProcessor[svcs.Container | None]` and already handles
both `Template` and `str | Markup` returns. Item 23 migrates all components across `tdom-svcs`
and `themester` to return `Template` directly — eliminating `Markup(f"...")` construction,
removing `context=` parameters from `__call__` methods, and dropping redundant inner `html()` calls.
The processor is unchanged during this migration.

**Goal:** All component `__call__` methods return `t"..."`. `get_view()` in themester converts
Template → str for its callers. Zero behavior change in rendered output.

---

## Task 1: Update Protocol Definitions

**Files:**
- `themester/src/themester/layouts/types.py` — `Layout.__call__() -> str` → `-> Template`
- `themester/src/themester/views/decorators.py` — update docstring examples `-> str` → `-> Template`

---

## Task 2: Migrate themester Production Code

**`themester/src/themester/views/__init__.py`** — Update `get_view()`:
- Remove context= branching; simplified: `view_instance = injector(view_impl, **kwargs)`, `template = view_instance()`
- Call `html(template, container=container)` to convert Template → str
- Import `html` from `tdom_svcs`

**`themester/src/themester/cli/layout_generate.py`** — Update generated code to return `t"..."`.

**`themester/src/themester/layouts/decorators.py`** — Update docstring examples.

---

## Task 3: Migrate tdom-svcs Examples (~17 files)

Pattern: `-> str | Markup: return Markup(f"...")` → `-> Template: return t"..."`

Files:
- `examples/common/components.py`
- `examples/basic/function_dataclass_poco.py`, `pure_tdom.py`, `props_priority.py`, `inject_service.py`
- `examples/hopscotch/basic_container.py`, `resource/`, `app_site/`, `location/`, `override/`
- `examples/middleware/aria/components.py`

---

## Task 4: Migrate tdom-svcs Tests (~4 files)

- `tests/test_di_injection.py`
- `tests/test_context_config_passing.py`
- `tests/test_register_implementation.py`
- `tests/test_introspection.py`

---

## Task 5: Migrate themester Examples

Files in `themester/examples/` with `__call__(self) -> str`.

---

## Task 6: Migrate themester Tests

Files in `themester/tests/` with component `__call__` returning str.
Remove `context=None` params; update return types and bodies.

---

## Verification

1. `astral:ty` on `tdom-svcs/src/` and `themester/src/`
2. `astral:ruff` on both packages
3. `uv run pytest tests/` in both packages
