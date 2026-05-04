# tdom-svcs Kind Metadata Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate tdom-svcs middleware and hookable discovery documentation/tests from role categories to first-class Hopscotch kinds.

**Architecture:** tdom-svcs continues to re-export Hopscotch's `middleware`, `hookable`, `register_middleware`, `register_hookable`, and `get_middleware_types()` behavior. The code path already stores `kind` in svcs-hopscotch; this package updates its expectations and examples so role discovery uses `get_by_kind()` while user facets remain in `categories`.

**Tech Stack:** Python 3.14, uv workspace, svcs-hopscotch, pytest, Ruff, ty.

---

## File Structure

- Modify `tests/test_categories.py`: assert role metadata via `kind`, role discovery via `get_by_kind()`, and user categories via `get_by_category()`.
- Modify `examples/categories/categories_example.py`: query all middleware and hookables by kind while keeping user category queries.
- Modify `src/tdom_svcs/scanning.py`: update docstrings from category-role discovery to injectable kind discovery.
- Modify current docs that describe role categories: `docs/api_reference.md`, `docs/categories.md`, `docs/examples/categories/*.md`, and any current docs found by `rg`.

## Task 1: Tests

**Files:**
- Modify: `tests/test_categories.py`

- [ ] **Step 1: Update metadata tests**

Change assertions so `@middleware` and `@hookable` prove role metadata is stored in `kind`:

```python
assert metadata["kind"] == "middleware"
assert metadata["categories"] is None
```

For user categories:

```python
assert metadata["kind"] == "middleware"
assert metadata["categories"] == ("security", "auth")
```

For hookable:

```python
assert metadata["kind"] == "hookable"
assert metadata["categories"] is None
```

- [ ] **Step 2: Update discovery tests**

Change role queries to `get_by_kind()` and keep user facet category checks:

```python
assert SecurityLogger in registry.get_by_kind("middleware")
assert SecurityLogger not in registry.get_by_category("middleware")
assert SecurityLogger in registry.get_by_category("security")
```

For hookables:

```python
assert Button in registry.get_by_kind("hookable")
assert Button not in registry.get_by_category("hookable")
assert Button in registry.get_by_category("widget")
```

- [ ] **Step 3: Run tests and verify RED**

Run:

```bash
uv run pytest tests/test_categories.py
```

Expected before updates are complete: failures should point at role category assumptions, not import or syntax errors.

- [ ] **Step 4: Run tests and verify GREEN**

Run:

```bash
uv run pytest tests/test_categories.py
```

Expected: selected tests pass.

## Task 2: Examples and Docs

**Files:**
- Modify: `examples/categories/categories_example.py`
- Modify: `src/tdom_svcs/scanning.py`
- Modify: relevant `docs/**/*.md` files found by role-category search

- [ ] **Step 1: Update category example role queries**

Use kind-based discovery for role groups:

```python
all_middleware = list(registry.get_by_kind("middleware"))
all_hookables = list(registry.get_by_kind("hookable"))
```

Keep user facets such as `security` and `page` as `get_by_category(...)`.

- [ ] **Step 2: Update docs**

Replace current role-category wording with kind-based role discovery and user-category facets. Leave historical Superpowers specs alone unless they are part of this migration.

- [ ] **Step 3: Search for stale role-category references**

Run:

```bash
rg -n 'get_by_category\("(middleware|hookable)"|categories=.*("middleware"|"hookable")|category-based.*(middleware|hookable)|role categor' src tests examples docs -g '!docs/_build/**' -g '!docs/superpowers/specs/**'
```

Expected: no current code/docs teach role categories as the primary middleware/hookable discovery path. Negative assertions in tests are acceptable.

## Task 3: Verification

**Files:**
- No additional files expected.

- [ ] **Step 1: Run tests**

Run:

```bash
just test
```

Expected: all tests pass.

- [ ] **Step 2: Run quality**

Run:

```bash
just quality
```

Expected: Ruff, formatting, and ty pass.

- [ ] **Step 3: Check diff hygiene**

Run:

```bash
git diff --check
git status --short
```

Expected: no whitespace errors; status shows only intentional changes.
