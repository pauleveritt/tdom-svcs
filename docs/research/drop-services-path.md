# Drop `services/path/` -- Migration to tdom-assets

## Summary

All asset management responsibilities have been consolidated into `tdom-assets`,
an svcs-native package in the workspace. `tdom-svcs/services/path/` can be
removed entirely. tdom-svcs does NOT need a dependency on tdom-assets -- the
explicit hook approach (`AssetCollector.use()`) means asset management is fully
decoupled from the rendering middleware pipeline.

## What to Remove

### `services/path/` directory (entire)

| File | What it contains | Why it's safe to remove |
|------|-----------------|------------------------|
| `collector.py` | `PathCollector` service | Replaced by `tdom_assets.AssetCollector` |
| `middleware.py` | `PathMiddleware` | Retired -- `collector.use()` replaces middleware interception |
| `types.py` | `ComponentLocation`, `AssetReference` | Canonical versions now in `tdom_assets.types` |
| `__init__.py` | Re-exports | No longer needed |

### From `tdom_svcs/types.py`

Remove the `COMPONENT_LOCATION_PROP` constant. It was used by `PathMiddleware`
to store `ComponentLocation` in component props during rendering. Since
`PathMiddleware` is retired, this constant has no consumers.

### Tests

Remove all tests for `services/path/` (they test PathCollector, PathMiddleware,
and the types that are now canonical in tdom-assets).

## What NOT to Remove

Everything else in tdom-svcs is unaffected:

- `html()` function -- still used by themester and components
- Other services (if any) -- not related to path/asset management
- Middleware infrastructure -- only `PathMiddleware` is removed, not the middleware system

## Why This Is Safe

1. **tdom-assets has complete test coverage** for all migrated functionality
2. **themester is already migrated** (branch `migrate-to-tdom-assets`) -- all 184 tests pass
3. **No other workspace packages** import from `tdom_svcs.services.path`
4. The explicit hook approach is **simpler** -- no middleware interception during rendering

## API Mapping for Consumers

### Import Changes

```python
# Old
from tdom_svcs.services.path import PathCollector, AssetReference, ComponentLocation

# New
from tdom_assets import AssetCollector, AssetReference, ComponentLocation
```

### Method Changes

```python
# Old: register an asset with string path
location = path_collector.register_component(MyComponent)
path_collector.register_asset(location, "./static/styles.css")

# New: explicit hook with PurePosixPath
from pathlib import PurePosixPath
collector.use(MyComponent, PurePosixPath("./static/styles.css"))
```

```python
# Old: scan HTML for assets
path_collector.collect_from_node(rendered_html, component_location)

# New: same concept, clearer name
collector.collect_from_html(rendered_html, component_location)
```

### Service Registration

```python
# Old: manual factory registration
registry.register_factory(PathCollector, PathCollector)

# New: scan discovers @injectable + convention function registers default strategy
import tdom_assets
scan(registry, tdom_assets)
```

### Type Changes

- `AssetReference.relative_path` is now `PurePosixPath` (was `str`)
- `PurePosixPath("./static/styles.css")` normalizes to `PurePosixPath("static/styles.css")` -- the `./` prefix is stripped
- Use `str(asset.relative_path)` when you need the string form

### Rewriting and Copying

```python
# Old (in themester): local functions
from themester.ssg.build import rewrite_asset_paths, copy_all_assets
rewrite_asset_paths(html, assets, depth=2)
copy_all_assets(assets, output_dir)

# New: tdom-assets with strategy protocol
from tdom_assets import rewrite_asset_paths, copy_assets, RelativePrefixStrategy
rewrite_asset_paths(html, assets, PurePosixPath("docs/guide"), RelativePrefixStrategy())
copy_assets(assets, output_dir)
```

## Verification Checklist

After removing `services/path/`:

1. `uv run pytest tests/` in tdom-svcs -- no import errors
2. `uv run pytest tests/` in themester (on `migrate-to-tdom-assets` branch) -- all pass
3. `uv run pytest tests/` in tdom-assets -- all pass
4. No grep hits for `tdom_svcs.services.path` in any workspace package
