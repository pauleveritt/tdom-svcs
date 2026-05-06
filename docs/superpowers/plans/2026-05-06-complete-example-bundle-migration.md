# Complete Example Bundle Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate every `docs/examples/**` page from `literalinclude` blocks to `tainie-tools` `example-snippet` and `example-source` directives.

**Architecture:** Add a static guard test that makes brittle example includes visible, then migrate docs in grouped passes: Basic, Categories, Hopscotch, and Middleware. Single-file examples use auto-discovered bundle ids with source markers; directory examples use `example.toml` manifests and bundle-scoped snippet references.

**Tech Stack:** Python 3.14, Sphinx/MyST, `tainie_tools.examples.sphinx`, pytest, uv, Ruff, ty.

**Commit Policy:** The local `AGENTS.md` says not to automatically commit while implementing a plan. Treat each task-end checkpoint as a review boundary; only run `git commit` if the user explicitly asks.

---

## File Structure

### Tests

- Create `tests/test_example_docs_migration.py`
  - Static guard against `literalinclude`, `:start-at:`, and `:end-at:` in `docs/examples/**`.
  - Inventory validation guard for `examples/**` manifests and snippets.

### Basic Examples

- Modify `examples/basic/pure_tdom.py`
- Modify `examples/basic/function_dataclass_poco.py`
- Modify `examples/basic/svcs_container.py`
- Modify `examples/basic/inject_service.py`
- Modify `examples/basic/props_priority.py`
- Modify matching pages under `docs/examples/basic/`

### Categories Examples

- Modify `examples/categories/categories_example.py`
- Modify `docs/examples/categories/imperative_categories.md`
- Modify `docs/examples/categories/organizing_with_categories.md`

### Hopscotch Examples

- Modify `examples/hopscotch/basic_container.py`
- Modify `examples/common/components.py`
- Modify these directories and docs:
  - `examples/hopscotch/resource/`
  - `examples/hopscotch/app_site/`
  - `examples/hopscotch/override/`
  - `examples/hopscotch/location/`
  - `examples/hopscotch/scan_decorators/`
  - `docs/examples/hopscotch/*.md`
- Create manifests:
  - `examples/hopscotch/app_site/example.toml`
  - `examples/hopscotch/override/example.toml`
  - `examples/hopscotch/location/example.toml`
  - `examples/hopscotch/scan_decorators/example.toml`

### Middleware Example

- Modify `examples/middleware/aria/`
- Modify `docs/examples/middleware/aria.md`
- Create `examples/middleware/aria/example.toml`

### Roadmap

- Modify `docs/superpowers/roadmap.md`
  - Mark item 48 `Complete Example Bundle Migration` complete only after final verification passes.

---

## Current Include Inventory

Remaining `literalinclude` docs pages:

- Basic: `function_dataclass_poco.md`, `inject_service.md`, `props_priority.md`, `pure_tdom.md`, `svcs_container.md`
- Categories: `imperative_categories.md`, `organizing_with_categories.md`
- Hopscotch: `app_site.md`, `basic_container.md`, `location.md`, `override.md`, `resource.md`, `scan_decorators.md`
- Middleware: `aria.md`

Use this syntax for migrated references:

```md
```{example-snippet} basic/pure_tdom.py#greeting-component
```

```{example-snippet} hopscotch-app-site:app.py#app-scan
```

```{example-source} hopscotch-app-site
:files: app.py, app_common.py, site.py
```
```

Single-file examples use the file path as the target. Directory bundles use the
manifest `id` before the colon.

---

### Task 1: Add Migration Guard Tests

**Files:**
- Create: `tests/test_example_docs_migration.py`

- [ ] **Step 1: Add failing static guard tests**

Create `tests/test_example_docs_migration.py`:

```python
"""Guards for example docs migrated to tainie-tools example directives."""

from pathlib import Path

from tainie_tools.examples import scan_example_bundles, validate_example_inventory

ROOT = Path(__file__).resolve().parents[1]
DOC_EXAMPLES = ROOT / "docs" / "examples"
EXAMPLES = ROOT / "examples"


def test_example_docs_do_not_use_literalinclude_anchors() -> None:
    banned_patterns = ("```{literalinclude}", ":start-at:", ":end-at:")
    violations: list[str] = []

    for path in sorted(DOC_EXAMPLES.rglob("*.md")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if any(pattern in line for pattern in banned_patterns):
                relative = path.relative_to(ROOT)
                violations.append(f"{relative}:{line_number}: {line.strip()}")

    assert violations == []


def test_example_inventory_has_no_validation_issues() -> None:
    inventory = scan_example_bundles(EXAMPLES)
    issues = validate_example_inventory(inventory)

    assert [issue.message for issue in issues] == []
```

- [ ] **Step 2: Run the new guard tests and confirm the expected failure**

Run:

```bash
uv run pytest tests/test_example_docs_migration.py -q
```

Expected: `test_example_docs_do_not_use_literalinclude_anchors` fails and lists the current `literalinclude`/anchor lines. The inventory validation test should pass or list manifest issues that must be fixed in later tasks.

- [ ] **Step 3: Run formatting and type checks for the new test**

Run:

```bash
uv run ruff check tests/test_example_docs_migration.py
uv run ruff format --check tests/test_example_docs_migration.py
uv run ty check tests/test_example_docs_migration.py
```

Expected: all three commands pass. If Ruff requests wrapping, run `uv run ruff format tests/test_example_docs_migration.py`, then rerun the checks.

- [ ] **Step 4: Review checkpoint**

Run:

```bash
git diff -- tests/test_example_docs_migration.py
```

Expected: one new static guard file; no example migrations yet.

---

### Task 2: Migrate Basic Examples

**Files:**
- Modify: `examples/basic/pure_tdom.py`
- Modify: `examples/basic/function_dataclass_poco.py`
- Modify: `examples/basic/svcs_container.py`
- Modify: `examples/basic/inject_service.py`
- Modify: `examples/basic/props_priority.py`
- Modify: `docs/examples/basic/pure_tdom.md`
- Modify: `docs/examples/basic/function_dataclass_poco.md`
- Modify: `docs/examples/basic/svcs_container.md`
- Modify: `docs/examples/basic/inject_service.md`
- Modify: `docs/examples/basic/props_priority.md`

- [ ] **Step 1: Add snippet markers to `pure_tdom.py`**

In `examples/basic/pure_tdom.py`, wrap the component and render call:

```python
# docs: start greeting-component
def Greeting(name: str = "World") -> Template:
    """Render a greeting with the given name."""
    return t"<h1>Hello {name}!</h1>"
# docs: end greeting-component
```

```python
# docs: start render-call
def main() -> str:
    response = html(t"<{Greeting} name='Alice' />")

    result = str(response)
    assert "Alice" in result

    return result
# docs: end render-call
```

- [ ] **Step 2: Migrate `pure_tdom.md`**

Replace all `literalinclude` blocks in `docs/examples/basic/pure_tdom.md` with:

```md
```{example-snippet} basic/pure_tdom.py#greeting-component
```
```

```md
```{example-snippet} basic/pure_tdom.py#render-call
```
```

For the full source section, use:

```md
```{example-source} basic/pure_tdom
```
```

- [ ] **Step 3: Add snippet markers to `function_dataclass_poco.py`**

Use these marker ids in `examples/basic/function_dataclass_poco.py`:

- `dataclass-component`: wrap the full existing `Greeting2` class from
  `@dataclass` through `return t"<h1>Hello {self.name}!</h1>"`.
- `poco-component`: wrap the full existing `Greeting3` class from
  `class Greeting3:` through `return t"<h1>Hello {self.name}!</h1>"`.
- `function-component`: wrap the full existing `Greeting1()` function from
  `def Greeting1(name: str = "World") -> Template:` through
  `return t"<h1>Hello {name}!</h1>"`.

Inside `main()`, wrap the three rendering sections with:

```python
# docs: start render-function
response1 = html(t"<{Greeting1} name='Alice' />")
result1 = str(response1)
assert "Alice" in result1
# docs: end render-function
```

```python
# docs: start render-dataclass
response2 = html(t"<{Greeting2} name='Alice' />")
result2 = str(response2)
assert "Alice" in result2
# docs: end render-dataclass
```

```python
# docs: start render-poco
response3 = html(t"<{Greeting3} name='Alice' />")
result3 = str(response3)
assert "Alice" in result3
# docs: end render-poco
```

- [ ] **Step 4: Migrate `function_dataclass_poco.md`**

Use these directives in `docs/examples/basic/function_dataclass_poco.md`:

```md
```{example-snippet} basic/function_dataclass_poco.py#function-component
```

```{example-snippet} basic/function_dataclass_poco.py#dataclass-component
```

```{example-snippet} basic/function_dataclass_poco.py#poco-component
```

```{example-snippet} basic/function_dataclass_poco.py#render-function
```

```{example-snippet} basic/function_dataclass_poco.py#render-dataclass
```

```{example-snippet} basic/function_dataclass_poco.py#render-poco
```

```{example-source} basic/function_dataclass_poco
```
```

- [ ] **Step 5: Add snippet markers to service-oriented Basic examples**

Use these marker names in `examples/basic/inject_service.py`:

- `users-service`: `Users` dataclass.
- `greeting-component`: `Greeting` dataclass.
- `registry-setup`: registry creation and service factory registration.
- `request-context`: request construction and local container registration.
- `render-component`: `html(...)`, `str(...)`, and assertion block.

Use these marker names in `examples/basic/props_priority.py`:

- `users-service`: `Users` dataclass.
- `greeting-component`: `Greeting` dataclass.
- `registry-setup`: registry creation and service factory registration.
- `explicit-prop`: explicit prop render/assert block.
- `injected-default`: container-derived render/assert block.

In `examples/basic/svcs_container.py`, use:

- `user-types`: `UserDict`, `Users`, and `DEFAULT_USERS`.
- `database-service`: `Database`.
- `service-dependency`: `Service`.
- `injected-component`: `Greeting`.
- `registry-setup`: registry creation and factory registration.
- `container-render`: container block and `html(...)` call.

- [ ] **Step 6: Migrate remaining Basic docs**

Replace `literalinclude` blocks with these targets:

`docs/examples/basic/inject_service.md`:

```md
```{example-snippet} basic/inject_service.py#users-service
```

```{example-snippet} basic/inject_service.py#greeting-component
```

```{example-snippet} basic/inject_service.py#registry-setup
```

```{example-snippet} basic/inject_service.py#request-context
```

```{example-snippet} basic/inject_service.py#render-component
```

```{example-source} basic/inject_service
```
```

`docs/examples/basic/props_priority.md`:

```md
```{example-snippet} basic/props_priority.py#users-service
```

```{example-snippet} basic/props_priority.py#greeting-component
```

```{example-snippet} basic/props_priority.py#registry-setup
```

```{example-snippet} basic/props_priority.py#explicit-prop
```

```{example-snippet} basic/props_priority.py#injected-default
```

```{example-source} basic/props_priority
```
```

For `props_priority.py`, wrap the explicit prop render as `explicit-prop` and
the container-derived render as `injected-default`.

`docs/examples/basic/svcs_container.md`:

```md
```{example-snippet} basic/svcs_container.py#user-types
```

```{example-snippet} basic/svcs_container.py#database-service
```

```{example-snippet} basic/svcs_container.py#service-dependency
```

```{example-snippet} basic/svcs_container.py#injected-component
```

```{example-snippet} basic/svcs_container.py#registry-setup
```

```{example-snippet} basic/svcs_container.py#container-render
```

```{example-source} basic/svcs_container
```
```

- [ ] **Step 7: Verify Basic migration**

Run:

```bash
uv run pytest tests/test_examples.py -q
uv run sphinx-build -W -b html docs docs/_build/html
rg '```\\{literalinclude\\}|:start-at:|:end-at:' docs/examples/basic
```

Expected: pytest and Sphinx pass. The `rg` command exits with code 1 and prints no Basic docs matches.

---

### Task 3: Migrate Categories Examples

**Files:**
- Modify: `examples/categories/categories_example.py`
- Modify: `docs/examples/categories/imperative_categories.md`
- Modify: `docs/examples/categories/organizing_with_categories.md`

- [ ] **Step 1: Add snippet markers to `categories_example.py`**

Use these marker ids:

- `decorator-middleware`: `AuthenticationMiddleware` and `ValidationMiddleware`.
- `decorator-hookables`: `AdminDashboard` and `Button`.
- `imperative-middleware`: `AuditMiddleware`.
- `imperative-hookable`: `PublicPage`.
- `scan-and-register`: scan plus imperative registration inside `main()`.
- `category-queries`: category, kind, security, hookable, and page queries.
- `middleware-execution`: container block that executes security middleware.

- [ ] **Step 2: Migrate Categories docs**

Use these directives in both category docs wherever the prose references the matching code:

```md
```{example-snippet} categories/categories_example.py#decorator-middleware
```

```{example-snippet} categories/categories_example.py#decorator-hookables
```

```{example-snippet} categories/categories_example.py#imperative-middleware
```

```{example-snippet} categories/categories_example.py#imperative-hookable
```

```{example-snippet} categories/categories_example.py#scan-and-register
```

```{example-snippet} categories/categories_example.py#category-queries
```

```{example-snippet} categories/categories_example.py#middleware-execution
```

```{example-source} categories/categories_example
```
```

- [ ] **Step 3: Verify Categories migration**

Run:

```bash
uv run pytest tests/test_examples.py -q
uv run sphinx-build -W -b html docs docs/_build/html
rg '```\\{literalinclude\\}|:start-at:|:end-at:' docs/examples/categories
```

Expected: pytest and Sphinx pass. The `rg` command exits with code 1 and prints no Categories docs matches.

---

### Task 4: Migrate Hopscotch Examples

**Files:**
- Modify: `examples/hopscotch/basic_container.py`
- Modify: `examples/common/components.py`
- Modify: `examples/hopscotch/resource/resources.py`
- Modify: `examples/hopscotch/resource/site/resources.py`
- Modify: `examples/hopscotch/app_site/app.py`
- Modify: `examples/hopscotch/app_site/app_common.py`
- Modify: `examples/hopscotch/app_site/site.py`
- Modify: `examples/hopscotch/override/app.py`
- Modify: `examples/hopscotch/override/app_common.py`
- Modify: `examples/hopscotch/override/site.py`
- Modify: `examples/hopscotch/location/app.py`
- Modify: `examples/hopscotch/location/components.py`
- Modify: `examples/hopscotch/location/site/components.py`
- Modify: `examples/hopscotch/scan_decorators/app.py`
- Modify: `examples/hopscotch/scan_decorators/site/__init__.py`
- Modify: `examples/hopscotch/scan_decorators/site/components.py`
- Create: `examples/hopscotch/app_site/example.toml`
- Create: `examples/hopscotch/override/example.toml`
- Create: `examples/hopscotch/location/example.toml`
- Create: `examples/hopscotch/scan_decorators/example.toml`
- Modify: `docs/examples/hopscotch/*.md`

- [ ] **Step 1: Finish `hopscotch/resource` pilot**

Add snippet markers:

In `examples/hopscotch/resource/resources.py`:

- `default-resource`: wrap the resource definitions from `class Customer`
  through the end of `DefaultCustomer`.

In `examples/hopscotch/resource/site/resources.py`:

- `french-resource`: wrap the full `FrenchCustomer` class.

Replace the two remaining `literalinclude` blocks in `docs/examples/hopscotch/resource.md` with:

```md
```{example-snippet} hopscotch-resource:resources.py#default-resource
```

```{example-snippet} hopscotch-resource:site/resources.py#french-resource
```
```

- [ ] **Step 2: Migrate single-file `basic_container`**

In `examples/hopscotch/basic_container.py`, add snippet markers:

- `registry-setup`: `registry = HopscotchRegistry()`.
- `container-context`: `with HopscotchContainer(registry) as container:`.
- `scan-call`: the `scan(registry, locals_dict=globals())` line.
- `database-service`: `Database` class.
- `users-service`: `Users` class.
- `greeting-component`: `Greeting` class.

Replace `docs/examples/hopscotch/basic_container.md` includes with:

```md
```{example-snippet} hopscotch/basic_container.py#registry-setup
```

```{example-snippet} hopscotch/basic_container.py#container-context
```

```{example-snippet} hopscotch/basic_container.py#scan-call
```

```{example-snippet} hopscotch/basic_container.py#database-service
```

```{example-snippet} hopscotch/basic_container.py#users-service
```

```{example-snippet} hopscotch/basic_container.py#greeting-component
```

```{example-source} hopscotch/basic_container
```
```

- [ ] **Step 3: Add Hopscotch bundle manifests**

Create `examples/hopscotch/app_site/example.toml`:

```toml
id = "hopscotch-app-site"
title = "App And Site Scanning"
summary = "Shows app/site module scanning with shared application components."
entrypoint = "app.py"
concepts = ["component-override"]
proves = ["scan-discovers-decorators"]
```

Create `examples/hopscotch/override/example.toml`:

```toml
id = "hopscotch-override"
title = "Imperative Component Override"
summary = "Shows explicit site-level component replacement with register_implementation."
entrypoint = "app.py"
concepts = ["component-override"]
proves = ["component-implementation-selection"]
```

Create `examples/hopscotch/location/example.toml`:

```toml
id = "hopscotch-location"
title = "Location-Based Component Resolution"
summary = "Shows component selection that varies by container location."
entrypoint = "app.py"
concepts = ["component-override"]
proves = ["component-implementation-selection"]
```

Create `examples/hopscotch/scan_decorators/example.toml`:

```toml
id = "hopscotch-scan-decorators"
title = "Scanning For Decorators"
summary = "Shows decorator-based component override discovery through scan()."
entrypoint = "app.py"
concepts = ["component-override"]
proves = ["scan-discovers-decorators"]
```

If Sphinx reports unknown domain ids, remove the unknown id from the manifest
rather than inventing new domain ids in this task.

- [ ] **Step 4: Add Hopscotch bundle snippet markers**

Use these marker ids:

`examples/hopscotch/app_site/app.py`:

- `app-scan`: registry creation and `scan(registry, app_common, site)`.
- `render-component`: container block with request registration and `html(...)`.

`examples/hopscotch/app_site/app_common.py`:

- `base-component`: `Greeting` class.
- `base-services`: `Request`, `UserDict`, `UsersDict`, `DEFAULT_USERS`, `Database`, and `Users`.

`examples/hopscotch/app_site/site.py`:

- `site-registry`: `svcs_registry()`.

`examples/hopscotch/override/app.py`:

- `app-scan`: registry creation and scan call.
- `render-override`: container block and assertions proving `Bonjour`.

`examples/hopscotch/override/app_common.py`:

- `base-component`: `Greeting` class.
- `base-services`: `Database` and `Users`.

`examples/hopscotch/override/site.py`:

- `override-component`: `FrenchGreeting`.
- `register-override`: `svcs_registry()` registering the implementation.

`examples/hopscotch/location/app.py`:

- `default-request`: first container block.
- `french-request`: second container block.

`examples/hopscotch/location/components.py`:

- `base-greeting`: `Greeting`.

`examples/hopscotch/location/site/components.py`:

- `french-greeting`: `FrenchGreeting`.

`examples/common/components.py`:

- `greeting-component`: shared `Greeting` class.

`examples/hopscotch/scan_decorators/app.py`:

- `scan-app-site`: registry creation and scan call.

`examples/hopscotch/scan_decorators/site/__init__.py`:

- `site-registry`: `svcs_registry()`.

`examples/hopscotch/scan_decorators/site/components.py`:

- `decorated-override`: decorated `FrenchGreeting`.

- [ ] **Step 5: Migrate Hopscotch docs**

Use bundle-scoped references:

`docs/examples/hopscotch/app_site.md`:

```md
```{example-snippet} hopscotch-app-site:app.py#app-scan
```

```{example-snippet} hopscotch-app-site:app_common.py#base-component
```

```{example-snippet} hopscotch-app-site:site.py#site-registry
```

```{example-snippet} hopscotch-app-site:app.py#render-component
```

```{example-source} hopscotch-app-site
:files: app.py, app_common.py, site.py
```
```

`docs/examples/hopscotch/override.md`:

```md
```{example-snippet} hopscotch-override:app_common.py#base-component
```

```{example-snippet} hopscotch-override:site.py#override-component
```

```{example-snippet} hopscotch-override:site.py#register-override
```

```{example-snippet} hopscotch-override:app.py#app-scan
```

```{example-snippet} hopscotch-override:app.py#render-override
```

```{example-source} hopscotch-override
:files: app.py, app_common.py, site.py
```
```

`docs/examples/hopscotch/location.md`:

```md
```{example-snippet} hopscotch-location:app.py#default-request
```

```{example-snippet} hopscotch-location:app.py#french-request
```

```{example-snippet} hopscotch-location:site/components.py#french-greeting
```

```{example-snippet} hopscotch-location:components.py#base-greeting
```

```{example-source} hopscotch-location
:files: app.py, components.py, request.py, services.py, site/__init__.py, site/components.py
```
```

`docs/examples/hopscotch/scan_decorators.md`:

```md
```{example-snippet} common/components.py#greeting-component
```

```{example-snippet} hopscotch-scan-decorators:site/components.py#decorated-override
```

```{example-snippet} hopscotch-scan-decorators:site/__init__.py#site-registry
```

```{example-snippet} hopscotch-scan-decorators:app.py#scan-app-site
```

```{example-source} hopscotch-scan-decorators
:files: app.py, components.py, request.py, services.py, site/__init__.py, site/components.py
```
```

- [ ] **Step 6: Verify Hopscotch migration**

Run:

```bash
uv run pytest tests/test_examples.py -q
uv run sphinx-build -W -b html docs docs/_build/html
rg '```\\{literalinclude\\}|:start-at:|:end-at:' docs/examples/hopscotch
```

Expected: pytest and Sphinx pass. The `rg` command exits with code 1 and prints no Hopscotch docs matches.

---

### Task 5: Migrate Middleware ARIA Example

**Files:**
- Modify: `examples/middleware/aria/app.py`
- Modify: `examples/middleware/aria/components.py`
- Modify: `examples/middleware/aria/middleware.py`
- Modify: `examples/middleware/aria/services.py`
- Create: `examples/middleware/aria/example.toml`
- Modify: `docs/examples/middleware/aria.md`

- [ ] **Step 1: Add ARIA manifest**

Create `examples/middleware/aria/example.toml`:

```toml
id = "middleware-aria"
title = "ARIA Verifier Middleware"
summary = "Shows per-target middleware that inspects rendered HTML for missing image alt text."
entrypoint = "app.py"
concepts = []
proves = []
```

- [ ] **Step 2: Add ARIA snippet markers**

Use these marker ids:

`examples/middleware/aria/services.py`:

- `logger-service`: `Logger`.

`examples/middleware/aria/middleware.py`:

- `middleware-class`: `AriaVerifierMiddleware`.
- `image-check`: `_check_images()`.

`examples/middleware/aria/components.py`:

- `image-with-alt`: `ImageWithAlt`.
- `image-without-alt`: `ImageWithoutAlt`.

`examples/middleware/aria/app.py`:

- `registry-setup`: registry creation and scan call.
- `middleware-checks`: logger lookup, two `execute_target_middleware(...)` calls, and assertions.
- `render-target`: final `html(...)` call and return.

- [ ] **Step 3: Migrate `aria.md`**

Replace all `literalinclude` blocks in `docs/examples/middleware/aria.md` with:

```md
```{example-snippet} middleware-aria:services.py#logger-service
```

```{example-snippet} middleware-aria:middleware.py#middleware-class
```

```{example-snippet} middleware-aria:middleware.py#image-check
```

```{example-snippet} middleware-aria:components.py#image-with-alt
```

```{example-snippet} middleware-aria:components.py#image-without-alt
```

```{example-snippet} middleware-aria:app.py#registry-setup
```

```{example-snippet} middleware-aria:app.py#middleware-checks
```

```{example-snippet} middleware-aria:app.py#render-target
```

```{example-source} middleware-aria
:files: app.py, middleware.py, components.py, services.py
```
```

- [ ] **Step 4: Verify Middleware migration**

Run:

```bash
uv run pytest tests/test_examples.py -q
uv run sphinx-build -W -b html docs docs/_build/html
rg '```\\{literalinclude\\}|:start-at:|:end-at:' docs/examples/middleware
```

Expected: pytest and Sphinx pass. The `rg` command exits with code 1 and prints no Middleware docs matches.

---

### Task 6: Final Verification And Roadmap Completion

**Files:**
- Modify: `docs/superpowers/roadmap.md`

- [ ] **Step 1: Run the full migration guard**

Run:

```bash
uv run pytest tests/test_example_docs_migration.py -q
rg '```\\{literalinclude\\}|:start-at:|:end-at:' docs/examples
```

Expected: pytest passes. The `rg` command exits with code 1 and prints no matches.

- [ ] **Step 2: Run example and docs verification**

Run:

```bash
uv run pytest tests/test_examples.py -q
uv run sphinx-build -W -b html docs docs/_build/html
test -f docs/_build/html/example-inventory.json
```

Expected: all commands pass.

- [ ] **Step 3: Inspect generated inventory**

Run:

```bash
uv run python - <<'PY'
import json
from pathlib import Path

inventory = json.loads(Path("docs/_build/html/example-inventory.json").read_text())
print("\\n".join(sorted(inventory["bundles"])))
PY
```

Expected output includes at least:

```text
basic/function_dataclass_poco
basic/inject_service
basic/props_priority
basic/pure_tdom
basic/svcs_container
categories/categories_example
common/components
hopscotch-app-site
hopscotch-location
hopscotch-override
hopscotch-resource
hopscotch-scan-decorators
hopscotch/basic_container
middleware-aria
```

- [ ] **Step 4: Mark roadmap item 48 complete**

In `docs/superpowers/roadmap.md`, change the `Complete Example Bundle Migration` item from:

```md
48. [ ] P1 Complete Example Bundle Migration
```

to:

```md
48. [x] P1 Complete Example Bundle Migration
```

Add this completion note under that item:

```md
    Completed 2026-05-06: Basic, Categories, Hopscotch, and Middleware example
    docs now use `example-snippet` and `example-source` instead of brittle
    `literalinclude`, `:start-at:`, or `:end-at:` anchors. Multi-file examples
    have package-local `example.toml` manifests, Sphinx emits
    `example-inventory.json`, and the migration is guarded by
    `tests/test_example_docs_migration.py`.
```

- [ ] **Step 5: Run final quality checks**

Run:

```bash
just quality
just test
```

Expected: both commands pass.

- [ ] **Step 6: Review final diff**

Run:

```bash
git status --short
git diff --stat
```

Expected: changes are limited to the design/plan docs, example docs, example source markers, new manifests, the migration guard test, and roadmap item 48.

Do not commit unless the user explicitly asks for a commit.

---

## Self-Review

### Spec Coverage

- All `docs/examples/**` pages are covered by grouped tasks.
- Single-file examples use source markers and auto-discovered bundle ids.
- Multi-file Hopscotch and Middleware examples use `example.toml` manifests.
- Final verification includes example tests, Sphinx `-W`, inventory existence,
  no brittle anchors, and full project quality/tests.
- Roadmap completion is gated on verification.

### Placeholder Scan

The plan contains concrete file paths, marker ids, directive targets, manifest
contents, commands, and expected outcomes.

### Type Consistency

- Directive names are consistently `example-snippet` and `example-source`.
- Manifest ids are consistently used in matching docs targets.
- Snippet markers use the `# docs: start <id>` / `# docs: end <id>` syntax
  implemented by `tainie_tools.examples`.
