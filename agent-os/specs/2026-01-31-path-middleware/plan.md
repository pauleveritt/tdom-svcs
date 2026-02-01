# Path Middleware Implementation Plan

## Summary

Implement roadmap item #6: Path Middleware for tdom-svcs. Create a `PathCollector` service and middleware that tracks component locations and asset references during rendering.

**Key Design Decisions:**
- **Collection only** (no transformation) - simpler than tdom-path
- **Auto-detect assets** from `<link href>` and `<script src>` in component output
- **Colocated assets** - each component has its own `static/` subdirectory
- **Show collected data** - example prints what was gathered

---

## Task 1: Save Spec Documentation

Create `agent-os/specs/2026-01-31-path-middleware/` with:

- **plan.md** - This plan
- **shape.md** - Shaping notes (scope, decisions, context)
- **references.md** - Pointers to tdom-path specs and existing middleware examples

---

## Task 2: Implement PathCollector Service

Create `src/tdom_svcs/services/path/` with core service.

**Files:**
- `src/tdom_svcs/services/path/__init__.py` - Exports
- `src/tdom_svcs/services/path/collector.py` - PathCollector service
- `src/tdom_svcs/services/path/types.py` - ComponentLocation, AssetReference dataclasses

**Key Types:**
```python
@dataclass(frozen=True)
class ComponentLocation:
    component_type: type
    module_name: str
    file_path: Path

@dataclass(frozen=True)
class AssetReference:
    source: Traversable
    component_location: ComponentLocation
    relative_path: str          # Original: "./static/styles.css"
    module_path: PurePosixPath  # Resolved: "examples/middleware/path/head/static/styles.css"

@dataclass
class PathCollector:
    components: set[ComponentLocation]
    assets: set[AssetReference]

    def register_component(self, component: type) -> ComponentLocation
    def register_asset(self, component_location: ComponentLocation, relative_path: str) -> AssetReference
    def collect_from_node(self, node: Node, component_location: ComponentLocation) -> None
    def clear(self) -> None
```

**Auto-detection logic** (borrowed from tdom-path):
- Walk the Node tree looking for `<link href="...">` and `<script src="...">`
- Skip external URLs (http://, https://, //), special schemes (mailto:, data:, etc.)
- Register each found asset with the owning component's location

---

## Task 3: Implement PathMiddleware

Create middleware that registers components and auto-detects assets from their output.

**File:** `src/tdom_svcs/services/path/middleware.py`

```python
@dataclass
class PathMiddleware:
    collector: Inject[PathCollector]
    priority: int = 100  # Run late so we see the rendered Node

    def __call__(self, component, props, context) -> dict:
        # Register the component
        location = self.collector.register_component(component)

        # Store location so post-render can access it
        props["_component_location"] = location
        return props
```

**Note:** Asset collection happens when the component's Node is rendered, not during middleware. The middleware just tracks component locations.

---

## Task 4: Create Example

Create `examples/middleware/path/` with a full HTML page structure.

**Directory Structure:**
```
examples/middleware/path/
    __init__.py
    app.py                    # Main entry point
    components/
        __init__.py
        html_page.py          # HTML component using Head and Body
        head.py               # Head component with <link> and <script>
        body.py               # Body component
        head/
            static/
                styles.css    # Colocated CSS
                script.js     # Colocated JS
```

**Component Structure:**

```python
# head.py - Head component with colocated assets
@injectable
@dataclass
class Head:
    def __call__(self) -> Node:
        return html(t"""
            <head>
                <title>Path Middleware Example</title>
                <link rel="stylesheet" href="./static/styles.css">
                <script src="./static/script.js"></script>
            </head>
        """)

# body.py - Simple body component
@injectable
@dataclass
class Body:
    greeting: Inject[Greeting]

    def __call__(self) -> Node:
        return html(t"<body><{self.greeting} /></body>")

# html_page.py - Composes Head and Body
@injectable
@dataclass
class HTMLPage:
    head: Inject[Head]
    body: Inject[Body]

    def __call__(self) -> Node:
        return html(t"""
            <!DOCTYPE html>
            <html>
                <{self.head} />
                <{self.body} />
            </html>
        """)
```

**app.py output shows collected data:**
```python
def main() -> dict:
    # ... setup registry, container, middleware ...

    response = html(t"<{HTMLPage} />", context=container)
    collector = container.get(PathCollector)

    return {
        "html": str(response),
        "components": [
            {"name": loc.module_name, "file": str(loc.file_path)}
            for loc in collector.components
        ],
        "assets": [
            {
                "relative_path": ref.relative_path,
                "module_path": str(ref.module_path),
                "component": ref.component_location.module_name
            }
            for ref in collector.assets
        ]
    }
```

**Example output:**
```python
{
    "html": "<!DOCTYPE html><html>...",
    "components": [
        {"name": "examples.middleware.path.components.html_page", "file": "/..."},
        {"name": "examples.middleware.path.components.head", "file": "/..."},
        {"name": "examples.middleware.path.components.body", "file": "/..."}
    ],
    "assets": [
        {
            "relative_path": "./static/styles.css",
            "module_path": "examples/middleware/path/components/head/static/styles.css",
            "component": "examples.middleware.path.components.head"
        },
        {
            "relative_path": "./static/script.js",
            "module_path": "examples/middleware/path/components/head/static/script.js",
            "component": "examples.middleware.path.components.head"
        }
    ]
}
```

---

## Task 5: Write Tests

**File:** `tests/examples/middleware/test_path.py`

- Test PathCollector.register_component() returns correct location
- Test PathCollector.collect_from_node() finds link/script tags
- Test URL filtering (skips external, mailto:, etc.)
- Test example runs and returns expected structure
- Verify collected assets match actual files

---

## Task 6: Write Documentation

**File:** `docs/examples/middleware/path.md`

**Contents:**
1. Overview: What path collection does and why
2. Why relative paths during authoring (IDE tooling benefits)
3. Component structure with colocated assets
4. How auto-detection works (link href, script src)
5. PathCollector API reference
6. Full example walkthrough with output
7. Future: using collected data for build-time path rewriting

---

## Critical Files to Modify/Create

**New files:**
- `src/tdom_svcs/services/path/__init__.py`
- `src/tdom_svcs/services/path/collector.py`
- `src/tdom_svcs/services/path/types.py`
- `src/tdom_svcs/services/path/middleware.py`
- `examples/middleware/path/` (full directory structure above)
- `tests/examples/middleware/test_path.py`
- `docs/examples/middleware/path.md`

**Reference files (read for patterns):**
- `src/tdom_svcs/services/middleware/middleware_manager.py`
- `examples/middleware/basic/app.py`
- `/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py` - `_walk_tree`, `_should_process_href`, `AssetReference`

---

## Verification

1. Run example: `python -c "from examples.middleware.path.app import main; import json; print(json.dumps(main(), indent=2))"`
2. Run tests: `pytest tests/examples/middleware/test_path.py -v`
3. Verify:
   - PathCollector collects all 3 components (HTMLPage, Head, Body)
   - PathCollector collects 2 assets (styles.css, script.js)
   - Asset module_path correctly reflects colocated structure
   - Static files actually exist at the paths
