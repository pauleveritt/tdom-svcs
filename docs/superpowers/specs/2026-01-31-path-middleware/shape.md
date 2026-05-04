# Path Middleware - Shaping Notes

## Problem Context

tdom-path provides full path transformation capabilities - it rewrites relative asset paths in templates to absolute/relative paths for production. However, tdom-svcs needs a simpler approach: **collect** information about components and their assets without transforming them.

This enables:
- Build tooling to know which assets exist
- Dev servers to serve colocated static files
- Future: path rewriting as a separate concern

## Key Design Decisions

### 1. Collection Only (No Transformation)

**Decision:** PathCollector only collects; it doesn't modify the Node tree.

**Rationale:**
- Simpler to implement and test
- Transformation is a separate concern (use tdom-path for that)
- Collection data is useful for many purposes beyond path rewriting

### 2. Auto-Detection of Assets

**Decision:** Scan component output for `<link href>` and `<script src>` tags.

**Rationale:**
- Matches how tdom-path works
- No manual registration needed
- Catches all assets a component declares

### 3. Colocated Asset Structure

**Decision:** Each component can have a `static/` subdirectory for its assets.

**Example:**
```
components/
    head.py
    head/
        static/
            styles.css
            script.js
```

**Rationale:**
- IDE tooling works (relative paths resolve)
- Assets travel with components
- Clear ownership of assets

### 4. ComponentLocation Tracks Source

**Decision:** Store component type, module name, and file path.

**Rationale:**
- Need module name for module_path calculation
- Need file path for asset resolution
- Component type for identification

### 5. AssetReference Ties to Component

**Decision:** Each asset knows which component owns it.

**Rationale:**
- Enables per-component asset manifests
- Supports component-level caching
- Clear provenance for debugging

## Scope

### In Scope
- PathCollector service
- PathMiddleware for component tracking
- Auto-detection of link/script assets
- Example with colocated assets
- Basic tests

### Out of Scope
- Path transformation (use tdom-path)
- Asset bundling
- CSS/JS processing
- Image optimization
- Source maps

## Integration Points

### With Middleware System
- PathMiddleware registered like other middleware
- Uses MiddlewareManager for execution
- Can be combined with other middleware

### With svcs-di
- PathCollector registered as service
- Injected into PathMiddleware
- Available via container.get()

### With tdom
- Uses Node tree walking
- Detects Element tags
- Reads attributes from Elements

## Technical Approach

### URL Filtering
Reuse tdom-path's logic for filtering URLs:
```python
_EXTERNAL_URL_PATTERN = re.compile(
    r"^(https?://|//|mailto:|tel:|data:|javascript:|#)", re.IGNORECASE
)
```

### Module Path Calculation
```python
# From component module: examples.middleware.path.components.head
# Plus relative path: ./static/styles.css
# Yields: examples/middleware/path/components/head/static/styles.css
```

### Traversable for Asset Access
Use importlib.resources.abc.Traversable for cross-platform asset access that works with both filesystem and zipimport.
