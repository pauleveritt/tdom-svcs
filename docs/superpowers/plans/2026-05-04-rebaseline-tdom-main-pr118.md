# Rebaseline tdom-svcs Against tdom PR 118 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move `tdom-svcs` from the local `ian/integrations` processor API to merged `tdom` main after PR #118.

**Architecture:** Keep the existing `tdom_svcs.html(template, *, container=None)` public API and the container-as-field `DIComponentProcessor`. Rebase the processor integration to PR #118's non-generic `ComponentProcessor.process()` signature, preserve the four-phase Hopscotch Option C resolution flow, and remove component-object capture assumptions.

**Tech Stack:** Python 3.14, t-string `Template`, `tdom`/`tstring-html`, `svcs`, `svcs-di`, `svcs-hopscotch`, `uv`, `pytest`, `ruff`, `ty`, Sphinx/MyST.

---

## File Map

- Modify: `/Users/pauleveritt/projects/t-strings/tstring-html` checkout
  - Switch from local `ian/integrations` to merged `origin/main`.
- Modify: `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/processor.py`
  - Update imports, method signatures, return types, and `TemplateProcessor.process()` calls for PR #118.
- Modify: `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_processor_unit.py`
  - Update protocol-satisfaction assertion from `IComponentProcessor[None]` to `IComponentProcessor`.
- Modify: `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_hopscotch_resolution.py`
  - Replace component-object capture test with factory-component rendering behavior test.
- Modify: `/Users/pauleveritt/projects/t-strings/tdom-svcs/docs/research/port-tstring-html-integrations-revisited.md`
  - Add PR #118 supersession note.
- Modify: `/Users/pauleveritt/projects/t-strings/tdom-svcs/docs/research/di-context-threading.md`
  - Update final examples to remove `app_state=None`, and add PR #118 note where needed.
- Modify carefully: `/Users/pauleveritt/projects/t-strings/tdom-svcs/docs/superpowers/roadmap.md`
  - Keep Phase 8 as history and item 37 authoritative.
  - Preserve any unrelated user edits, including the current uncommitted Phase 10 section if present.
- Inspect: all workspace members under `/Users/pauleveritt/projects/t-strings`
  - Grep for removed processor API usage and update executable hits found by the audit.

---

### Task 1: Move the Workspace tdom Checkout to Merged Main

**Files:**
- Modify checkout state: `/Users/pauleveritt/projects/t-strings/tstring-html`
- Inspect: `/Users/pauleveritt/projects/t-strings/pyproject.toml`
- Inspect: `/Users/pauleveritt/projects/t-strings/uv.lock`

- [ ] **Step 1: Confirm current tdom checkout and remotes**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tstring-html
git status --short --branch
git remote -v
git log --oneline --decorate -5
```

Expected before switching:

```text
## ian/integrations...ian/ian/integrations
```

The remote list must include:

```text
origin  https://github.com/t-strings/tdom.git (fetch)
ian     https://github.com/ianjosephwilson/tdom.git (fetch)
```

- [ ] **Step 2: Fetch merged main**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tstring-html
git fetch origin main --tags
git rev-parse --short origin/main
```

Expected:

```text
b2287f1
```

- [ ] **Step 3: Switch the local checkout to merged main**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tstring-html
git switch main
git pull --ff-only origin main
git status --short --branch
```

Expected:

```text
## main...origin/main
```

If the local `main` has local commits and cannot fast-forward, do not reset it. Instead run:

```bash
cd /Users/pauleveritt/projects/t-strings/tstring-html
git switch -c codex/pr118-main origin/main
git status --short --branch
```

Expected fallback:

```text
## codex/pr118-main...origin/main
```

- [ ] **Step 4: Confirm PR #118 processor API is present**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tstring-html
rg -n "class IComponentProcessor|def process\\(|DefaultAppState|app_state|ComponentObject" tdom/processor.py
```

Expected:

```text
tdom/processor.py:class IComponentProcessor(t.Protocol):
tdom/processor.py:class ComponentProcessor(IComponentProcessor):
```

Expected absence:

```text
DefaultAppState
app_state
```

- [ ] **Step 5: Commit only if the checkout switch created tracked metadata changes**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings
git status --short
```

If only checkout state changed inside `tstring-html`, there may be no root git diff to commit. If `uv.lock` or workspace metadata changed after a later `uv sync`, commit that in the task where it changes.

---

### Task 2: Update tdom-svcs Processor Signature and Delegation

**Files:**
- Modify: `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/processor.py`

- [ ] **Step 1: Run the focused failure before editing**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
uv run pytest tests/test_processor_unit.py tests/test_hopscotch_resolution.py -q
```

Expected before the implementation changes:

```text
ImportError: cannot import name 'ComponentObject'
```

or:

```text
ImportError: cannot import name 'DefaultAppState'
```

- [ ] **Step 2: Update the import block in `processor.py`**

Replace this import block:

```python
from tdom.processor import (
    Attribute,
    ComponentObject,
    ComponentProcessor,
    DefaultAppState,
    ProcessContext,
    TemplateProcessor,
    _prep_component_kwargs,
    _resolve_t_attrs,
    get_callable_info,
)
```

with:

```python
from tdom.processor import (
    Attribute,
    ComponentProcessor,
    ProcessContext,
    TemplateProcessor,
    _prep_component_kwargs,
    _resolve_t_attrs,
    get_callable_info,
)
```

- [ ] **Step 3: Update `DIComponentProcessor.process()` signature and body**

In `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/processor.py`, replace the entire `DIComponentProcessor.process()` method with:

```python
    def process(
        self,
        template: Template,
        last_ctx: ProcessContext,
        component_callable: object,
        attrs: tuple[TAttribute, ...],
        component_template: Template,
        provided_attrs: tuple[Attribute, ...] = (),
    ) -> Template:
        container = self.container
        if container is None:
            return super().process(
                template,
                last_ctx,
                component_callable,
                attrs,
                component_template,
                provided_attrs,
            )

        # Component-level locator override (Protocol -> impl).
        if isinstance(component_callable, type):
            component_callable = _get_implementation(container, component_callable)

        if not needs_dependency_injection(component_callable):
            return super().process(
                template,
                last_ctx,
                component_callable,
                attrs,
                component_template,
                provided_attrs,
            )

        # Phase 1: pre-prep partial kwargs (template attrs + provided + children, no raise).
        callable_info = get_callable_info(component_callable)
        partial_kwargs = _prep_component_kwargs(
            callable_info,
            _resolve_t_attrs(attrs, template.interpolations),
            children=component_template,
            provided_attrs=provided_attrs,
            raise_on_missing=False,
            raise_on_requires_positional=False,
        )

        # Phase 2: full Hopscotch resolution: Get[T, Attr], locator, adapters, defaults.
        field_infos = hopscotch_get_field_infos(component_callable)  # ty: ignore[invalid-argument-type]
        resolved = build_resolved_kwargs(
            field_infos,
            _make_resolver(container),
            partial_kwargs,
        )

        # Phase 3: the DI-fill delta: fields Hopscotch resolved that were not in kwargs.
        di_fill = tuple(
            (name, value)
            for name, value in resolved.items()
            if name not in partial_kwargs
        )

        # Phase 4: delegate invocation to upstream's component processor.
        return super().process(
            template,
            last_ctx,
            component_callable,
            attrs,
            component_template,
            di_fill + provided_attrs,
        )
```

- [ ] **Step 4: Update `html()` to call the new `TemplateProcessor.process()` signature**

Replace:

```python
    return tp.process(template, ProcessContext(), app_state=None)
```

with:

```python
    return tp.process(template, ProcessContext())
```

- [ ] **Step 5: Run processor-focused tests**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
uv run pytest tests/test_processor_unit.py tests/test_hopscotch_resolution.py -q
```

Expected at this point:

```text
FAILED tests/test_processor_unit.py::...
FAILED tests/test_hopscotch_resolution.py::test_component_object_capture_factory
```

The failures should now be test expectations about `IComponentProcessor[None]`, `app_state`, or component-object capture, not import errors from `processor.py`.

- [ ] **Step 6: Commit processor signature update**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
git add src/tdom_svcs/processor.py
git commit -m "Update processor for tdom PR 118 API"
```

---

### Task 3: Update Tests for Behavior Instead of Component Capture

**Files:**
- Modify: `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_processor_unit.py`
- Modify: `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_hopscotch_resolution.py`

- [ ] **Step 1: Update protocol-satisfaction assertion**

In `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_processor_unit.py`, replace:

```python
# Protocol-satisfaction assertion: ty verifies DIComponentProcessor satisfies
# IComponentProcessor[None] (DefaultAppState) at type-check time.
_: IComponentProcessor[None] = DIComponentProcessor()
```

with:

```python
# Protocol-satisfaction assertion: ty verifies DIComponentProcessor satisfies
# tdom's non-generic IComponentProcessor protocol.
_: IComponentProcessor = DIComponentProcessor()
```

- [ ] **Step 2: Replace component-object capture test**

In `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_hopscotch_resolution.py`, replace the full test beginning with:

```python
# Scenario 7: component_object capture under DI (factory class)


def test_component_object_capture_factory():
```

through the final assertion:

```python
    assert factory_instances[0].svc.value == "test_value"
```

with:

```python
# Scenario 7: factory component rendering under DI


def test_factory_component_with_di_renders():
    """Factory component with Inject[T] fields renders via upstream invocation."""

    @dataclass
    class Service:
        value: str = "svc_value"

    @dataclass
    class FactoryComponent:
        svc: Inject[Service]

        def __call__(self) -> Template:
            return t"<p>{self.svc.value}</p>"

    registry = HopscotchRegistry()
    registry.register_value(Service, Service(value="test_value"))

    with HopscotchContainer(registry) as container:
        result = html(t"<{FactoryComponent} />", container=container)

    assert result == "<p>test_value</p>"
```

- [ ] **Step 3: Run focused tests**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
uv run pytest tests/test_processor_unit.py tests/test_hopscotch_resolution.py -q
```

Expected:

```text
passed
```

- [ ] **Step 4: Run full local tests**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
just test
```

Expected:

```text
passed
```

- [ ] **Step 5: Commit test updates**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
git add tests/test_processor_unit.py tests/test_hopscotch_resolution.py
git commit -m "Update tests for PR 118 processor API"
```

---

### Task 4: Run Workspace Impact Audit and Fix Executable Hits

**Files:**
- Inspect and possibly modify workspace members under `/Users/pauleveritt/projects/t-strings`
- Known likely files:
  - `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/processor.py`
  - `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_processor_unit.py`
  - `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_hopscotch_resolution.py`
  - `/Users/pauleveritt/projects/t-strings/themester`
  - `/Users/pauleveritt/projects/t-strings/storyville`

- [ ] **Step 1: Search the full workspace for old processor API**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
rg "DefaultAppState|IComponentProcessor\\[|TemplateProcessor\\[|app_state=|ComponentObject|component_object|processor_integration_test" ..
```

Expected after Tasks 2-3:

```text
```

Executable hits under `src/`, `tests/`, or examples should be absent or limited to docs/research files. If executable hits remain, continue with the next step.

- [ ] **Step 2: Classify each hit**

For every hit from Step 1, assign one of:

```text
EXECUTABLE: Python source, examples, or tests that import/call old API.
DOC-HISTORICAL: Research/roadmap text intentionally describing old API.
DOC-STALE: Documentation that presents old API as current.
```

Record the classification in the implementation notes or final response. The expected current historical docs include:

```text
docs/research/port-tstring-html-integrations-revisited.md
docs/research/di-context-threading.md
docs/superpowers/roadmap.md
docs/superpowers/specs/2026-05-04-rebaseline-tdom-main-pr118-design.md
```

- [ ] **Step 3: Update any executable hits**

If a Python call still uses:

```python
tp.process(template, ProcessContext(), app_state=None)
```

replace it with:

```python
tp.process(template, ProcessContext())
```

If a type assertion still uses:

```python
_: IComponentProcessor[None] = value
```

replace it with:

```python
_: IComponentProcessor = value
```

If an import still uses:

```python
from tdom.processor import ComponentObject, DefaultAppState
```

remove `ComponentObject` and `DefaultAppState` from the import list.

- [ ] **Step 4: Run checks for packages with executable hits**

For each package with executable hits, run its local test command. Use these commands as applicable:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
just test
```

```bash
cd /Users/pauleveritt/projects/t-strings/themester
just test
```

```bash
cd /Users/pauleveritt/projects/t-strings/storyville
uv run pytest
```

If a package lacks a `Justfile` or pytest configuration, run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-assets
uv run pytest
```

```bash
cd /Users/pauleveritt/projects/t-strings/aria-testing
uv run pytest
```

```bash
cd /Users/pauleveritt/projects/t-strings/tainie
uv run pytest
```

```bash
cd /Users/pauleveritt/projects/t-strings/svcs-di
uv run pytest
```

```bash
cd /Users/pauleveritt/projects/t-strings/svcs-hopscotch
uv run pytest
```

Expected for packages touched by executable fixes:

```text
passed
```

If a command fails because of a known unrelated issue, capture the first failing import or traceback line and continue with the remaining targeted checks.

- [ ] **Step 5: Commit executable audit fixes**

If Step 3 modified files, commit those exact files:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
git status --short
git add src/tdom_svcs/processor.py tests/test_processor_unit.py tests/test_hopscotch_resolution.py
git commit -m "Fix workspace PR 118 API references"
```

If Step 3 modified files outside `tdom-svcs`, commit those in their owning git
repository with exact `git add path/to/file.py` commands from `git status --short`.
If Step 3 did not modify files, do not create an empty commit.

---

### Task 5: Refresh Research Docs and Current Comments

**Files:**
- Modify: `/Users/pauleveritt/projects/t-strings/tdom-svcs/docs/research/port-tstring-html-integrations-revisited.md`
- Modify: `/Users/pauleveritt/projects/t-strings/tdom-svcs/docs/research/di-context-threading.md`
- Modify carefully: `/Users/pauleveritt/projects/t-strings/tdom-svcs/docs/superpowers/roadmap.md`
- Modify if needed: `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/processor.py`

- [ ] **Step 1: Add supersession note to `port-tstring-html-integrations-revisited.md`**

Add this note immediately after the opening title/date block:

```markdown
> **Superseded API note (2026-05-04):** tdom PR #118 merged after this analysis
> and removed `app_state`, `DefaultAppState`, generic `IComponentProcessor[T]`, and
> component-object capture from the current processor extension API. The Option C
> Hopscotch resolution strategy remains the chosen tdom-svcs approach, but current
> implementation must target PR #118's non-generic `ComponentProcessor.process()`
> signature and `Template` return value.
```

- [ ] **Step 2: Add supersession note to `di-context-threading.md`**

Add this note immediately after the `# DI Context Threading: Architecture Analysis` heading:

```markdown
> **PR #118 update (2026-05-04):** The container-as-field and per-container
> `TemplateProcessor` decision still stands. tdom PR #118 removed the `app_state`
> argument from `TemplateProcessor.process()`, so final code snippets should call
> `tp.process(template, ProcessContext())` rather than passing `app_state=None`.
```

- [ ] **Step 3: Update final snippets in `di-context-threading.md`**

Search:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
rg -n "app_state=None|tp\\.process\\(" docs/research/di-context-threading.md
```

For current end-state snippets that present active architecture, replace:

```python
return tp.process(template, ProcessContext(), app_state=None)
```

with:

```python
return tp.process(template, ProcessContext())
```

Leave old historical examples unchanged if they are explicitly discussed as historical upstream patterns.

- [ ] **Step 4: Update roadmap item 37 only if it still lacks the workspace audit**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
rg -n "Workspace Impact Audit|Rebaseline tdom-svcs Processor for PR #118" docs/superpowers/roadmap.md
git diff -- docs/superpowers/roadmap.md
```

If `docs/superpowers/roadmap.md` has unrelated user edits, preserve them. Only edit the Phase 9/item 37 text if it contradicts the spec. Do not stage unrelated Phase 10 or backlog changes unless they are part of this task.

- [ ] **Step 5: Verify processor comments no longer claim component-object capture**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
rg -n "component_object|ComponentObject|captures component" src/tdom_svcs/processor.py tests
```

Expected:

```text
```

If a current-code comment says `super().process()` captures component objects, remove or replace it with:

```python
# Phase 4: delegate invocation to upstream's component processor.
```

- [ ] **Step 6: Build docs**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
uv run sphinx-build -W -b html docs docs/_build/html
```

Expected:

```text
build succeeded.
```

- [ ] **Step 7: Commit docs refresh**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
git add docs/research/port-tstring-html-integrations-revisited.md docs/research/di-context-threading.md
git add src/tdom_svcs/processor.py tests/test_hopscotch_resolution.py
git add -p docs/superpowers/roadmap.md
git commit -m "Document PR 118 processor rebaseline"
```

Before committing, run:

```bash
git diff --cached --name-only
```

Expected staged files should be limited to files intentionally changed in this task. If unrelated roadmap changes are staged, unstage them with:

```bash
git restore --staged docs/superpowers/roadmap.md
git add -p docs/superpowers/roadmap.md
```

---

### Task 6: Run Final Verification

**Files:**
- No source edits expected.
- Inspect: workspace root `/Users/pauleveritt/projects/t-strings`

- [ ] **Step 1: Run final local quality**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
just quality
```

Expected:

```text
ruff check src tests
ruff format --check src tests
ty check
```

and all commands pass.

- [ ] **Step 2: Run final local tests**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
just test
```

Expected:

```text
passed
```

- [ ] **Step 3: Run docs build**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
just docs-build
```

Expected:

```text
build succeeded.
```

- [ ] **Step 4: Run downstream themester smoke**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/themester
just test
```

Expected:

```text
passed
```

If `just test` is not available, run:

```bash
cd /Users/pauleveritt/projects/t-strings/themester
uv run pytest
```

- [ ] **Step 5: Run workspace-wide removed API grep**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
rg "DefaultAppState|IComponentProcessor\\[|TemplateProcessor\\[|app_state=|ComponentObject|component_object|processor_integration_test" ..
```

Expected:

```text
```

or only historical docs/spec hits that explicitly mark the API as superseded.

- [ ] **Step 6: Try root workspace test if available**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings
uv run pytest
```

Expected:

```text
passed
```

If this fails because of a known unrelated workspace plugin/import issue, capture the first error line and include it in the final implementation report. Continue only if `tdom-svcs` and targeted downstream checks passed.

- [ ] **Step 7: Commit verification-only metadata if needed**

If verification changed only caches or build output ignored by git, do not commit. If verification required a small committed fix, stage exact files and commit:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
git status --short
git add src/tdom_svcs/processor.py tests/test_processor_unit.py tests/test_hopscotch_resolution.py docs/research/port-tstring-html-integrations-revisited.md docs/research/di-context-threading.md
git commit -m "Fix PR 118 rebaseline verification fallout"
```

---

### Task 7: Final Review and Handoff

**Files:**
- Inspect git state in:
  - `/Users/pauleveritt/projects/t-strings/tdom-svcs`
  - `/Users/pauleveritt/projects/t-strings/tstring-html`

- [ ] **Step 1: Check final git state**

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tdom-svcs
git status --short --branch
git log --oneline -5
```

Expected:

```text
## main...origin/main [ahead N]
```

Only unrelated pre-existing user edits may remain unstaged.

Run:

```bash
cd /Users/pauleveritt/projects/t-strings/tstring-html
git status --short --branch
git log --oneline -3
```

Expected:

```text
## main...origin/main
b2287f1 Component Process API Remix (#118)
```

- [ ] **Step 2: Summarize changed files and verification**

Prepare final report with:

```text
Changed:
- src/tdom_svcs/processor.py: updated to PR #118 processor API.
- tests/test_processor_unit.py: non-generic IComponentProcessor assertion.
- tests/test_hopscotch_resolution.py: factory behavior test replaces capture test.
- docs/research/...: PR #118 supersession notes.

Verified:
- just quality
- just test
- just docs-build
- themester test/smoke command
- workspace grep for removed API
- root workspace pytest result or explicit blocker
```

- [ ] **Step 3: Stop before merging or pushing**

Do not merge, push, or create a PR unless the user explicitly asks.
