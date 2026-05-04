# Item 22 — Cleanup tdom-svcs Against Current Upstream

## Context

tdom-svcs currently accepts `object | None` as the context argument to `html()`, supporting plain dicts,
arbitrary objects, and DI containers. This was a legacy design. The architecture decision (documented in
`docs/research/port-tstring-html-integrations.md`) is that `app_state` IS the `svcs.Container` (or `None`)
— nothing else. Stage 1 encodes that decision in the type system and removes all dead code paths that
handled other types, shrinking the fork before the larger port in Stage 3.

**Goal:** Mechanical type/dead-code cleanup. No behavior changes for callers passing `svcs.Container` or `None`.

---

## Task 1: Delete `types.py`

**File:** `src/tdom_svcs/types.py`

The file contains only `DIContainer` Protocol and `is_di_container` TypeGuard — both are being removed.
Delete the file entirely. No other module in the package re-exports from it.

---

## Task 2: Update `processor.py`

**File:** `src/tdom_svcs/processor.py`

Changes (all mechanical, no logic changes):

1. **Line 33** — Remove import: `from tdom_svcs.types import is_di_container`
2. **Line 35** — Remove: `type ContextArg = object | None`
3. **Line 38** — Update ContextVar type: `_di_context: ContextVar[svcs.Container | None]`
4. **Line 49** — Update `_get_implementation` signature: `context: svcs.Container | None`
5. **Line 51** — Replace guard: `if not is_di_container(context):` → `if context is None:`
6. **Line 150** — Replace guard: `is_di_container(context)` → `context is not None`
7. **Lines 198–202** — Rename parameter: `context: ContextArg = None` → `container: svcs.Container | None = None`
8. **Line 211** — Update ContextVar set: `_di_context.set(context)` → `_di_context.set(container)`
9. **Docstring** — Update `html()` docstring: replace `context` with `container`

The `_process_component` body is unchanged — the local `context = _di_context.get()` remains
(it is an internal variable, not the public parameter).

---

## Task 3: Update `test_html_wrapper.py`

**File:** `tests/test_html_wrapper.py`

- Remove the two dict-context parametrize cases (lines 19–25: `{"key": "value"}` cases)
- Remove the `@pytest.mark.parametrize` decorator entirely (only `None` case remains)
- Simplify `test_html_with_context` to a plain function calling `html(template)` without parametrize

---

## Task 4: Update `test_context_config_passing.py`

**File:** `tests/test_context_config_passing.py`

**Delete** these tests (test dict-specific behavior being removed):
- `test_is_di_container` — tests the deleted TypeGuard
- `test_is_di_container_with_hopscotch` — tests the deleted TypeGuard
- `test_dict_context_passed_but_no_di` — explicitly tests dict context
- `test_function_component_inject_with_dict_context_fails` — explicitly tests dict context

**Update** these tests (replace dict context with `None`):
- `test_function_component_receives_context` — `ctx = {"user": "Alice"}` → `ctx = None`; assert `received_context is None`
- `test_dataclass_component_receives_context` — same
- `test_component_without_context_param_ignores_it` — `ctx = {...}` → `container=None`
- `test_component_with_kwargs_receives_context` — `ctx = {...}` → `container=None`; update assertion
- `test_nested_components_receive_context` — `ctx = {...}` → `container=None`

**Rename** `context=` → `container=` in these calls:
- `test_component_receives_config_from_context` line 107
- `test_di_still_works_with_proper_container` line 160
- `test_di_component_call_receives_context_and_children` line 224
- `test_function_component_with_inject` line 247
- `test_function_component_with_multiple_inject` line 270

**Remove imports:**
- `from tdom_svcs.types import is_di_container`
- `CustomContainer` class

---

## Task 5: Update `docs/api_reference.md`

**File:** `docs/api_reference.md`

Update line 43 signature from:
```python
context: DIContainer | dict[str, Any] | None = None,
```
To:
```python
container: svcs.Container | None = None,
```

---

## Verification

1. Use `astral:ty` to type-check — expect 0 errors
2. Use `astral:ruff` to lint and format
3. Run `uv run pytest tests/` — all tests should pass
