# Path Collection and Rewriting

Component-based applications often colocate static assets (CSS, JavaScript) alongside their components. This works great during authoring—relative paths like `./static/styles.css` resolve correctly in IDEs. But these paths won't work in the browser because they're relative to the component's source file, not the request URL.

This example shows how middleware can solve this by tracking component locations during rendering and rewriting paths for browser consumption.

## The Problem

Consider a `Head` component with colocated assets:

```
components/
    head/
        head.py           # Component
        static/
            styles.css    # Component CSS
            script.js     # Component JS
```

The component references assets with relative paths:

```{literalinclude} ../../../examples/middleware/path/components/head/head.py
:start-at: def __call__
:end-at: )
```

During authoring, `./static/styles.css` resolves correctly because IDEs understand the path relative to `head.py`. But when the browser requests `/products/123`, a relative path `./static/styles.css` would resolve to `/products/static/styles.css`—which doesn't exist.

## The Solution

The `PathCollector` service tracks component locations during rendering. When a component is registered, we record:

- **Module name**: `examples.middleware.path.components.head`
- **File path**: The absolute path to the component's source file

When we scan the component's rendered output for `<link href>` and `<script src>` tags, we record each asset with:

- **Relative path**: `./static/styles.css` (as written in the template)
- **Module path**: `examples/middleware/path/components/head/static/styles.css` (derived from module name + relative path)

The module path provides a unique, stable identifier for the asset that can be used to construct browser-friendly URLs.

## Before and After

Running the example shows the transformation:

```bash
uv run python -m examples.middleware.path.app
```

**Before** — Author-friendly relative paths:

```html
<head>
    <link rel="stylesheet" href="./static/styles.css" />
    <script src="./static/script.js"></script>
</head>
```

**After** — Browser-friendly absolute paths:

```html
<head>
    <link rel="stylesheet" href="/_static/examples/middleware/path/components/head/static/styles.css" />
    <script src="/_static/examples/middleware/path/components/head/static/script.js"></script>
</head>
```

The rewriting function is straightforward:

```{literalinclude} ../../../examples/middleware/path/app.py
:start-at: def rewrite_paths
:end-at: return result
```

## How It Works

1. **Render the page** with relative paths intact
2. **Register components** with `PathCollector` as they're encountered
3. **Scan rendered output** for asset references using `collect_from_node()`
4. **Rewrite paths** using the collected module paths

```{literalinclude} ../../../examples/middleware/path/app.py
:lines: 55-67, 80-81
```

## Where Data Is Stored

The `PathCollector` maintains two sets:

- **`components`**: Set of `ComponentLocation` objects (component type, module name, file path)
- **`assets`**: Set of `AssetReference` objects (source traversable, component location, relative path, module path)

Both are stored in memory on the `PathCollector` instance, which is registered as a service in the DI container. This makes it available to middleware throughout the rendering process.

## Build-Time Integration

The collected data enables several build-time workflows:

**Asset copying**: The `source` field on each `AssetReference` is a `Traversable` that can read the file contents. Copy each asset to `build_output / asset.module_path`.

**Cache busting**: Generate content hashes and rewrite paths to include them: `styles.css` → `styles.a3b2c1.css`.

**Dev server routing**: Configure the dev server to serve requests like `/_static/module/path/file.css` from the original source location.

## Full Source

```{literalinclude} ../../../examples/middleware/path/app.py
```
