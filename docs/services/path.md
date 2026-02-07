# Path Collection Service

The `PathCollector` service tracks component locations during rendering and collects static asset references from rendered HTML.

## Overview

Path collection enables:

- **Component Location Tracking**: Know where each component is defined in your codebase
- **Static Asset Discovery**: Automatically find CSS, JavaScript, and other static files referenced in components
- **Path Rewriting**: Convert relative paths to absolute URLs for browser consumption

## PathCollector Service

The `PathCollector` class provides methods for tracking and collecting paths:

```python
from tdom_svcs.services.path import PathCollector

# Create and register the collector
collector = PathCollector()
registry.register_value(PathCollector, collector)

# During rendering
with container:
    # Register component location
    location = collector.register_component(MyComponent)

    # Render and collect assets
    component = container.get(MyComponent)
    node = component()
    collector.collect_from_node(node, location)

    # Access collected assets
    for asset in collector.assets:
        print(f"{asset.relative_path} -> {asset.module_path}")
```

## ComponentLocation

Tracks where a component is defined:

```python
@dataclass(frozen=True)
class ComponentLocation:
    """Immutable record of where a component is defined."""

    component_type: type
    module_path: Path

    def __hash__(self) -> int:
        return hash((self.component_type, self.module_path))
```

## AssetReference

Records a static asset discovered during rendering:

```python
@dataclass(frozen=True)
class AssetReference:
    """Reference to a static asset in rendered HTML."""

    relative_path: str      # Path as written in HTML (e.g., "./static/styles.css")
    module_path: Path       # Resolved absolute path to asset
    component_location: ComponentLocation  # Which component referenced it
```

## Usage Pattern

### 1. Setup

Register the collector as a singleton service:

```python
from tdom_svcs.services.path import PathCollector

collector = PathCollector()
registry.register_value(PathCollector, collector)
```

### 2. Component Registration

Before rendering, register each component's location:

```python
from pathlib import Path
import inspect

# Get component's module path
module_file = inspect.getfile(MyComponent)
module_path = Path(module_file).parent

# Register with collector
location = collector.register_component(MyComponent)
```

### 3. Asset Collection

After rendering, scan the HTML for asset references:

```python
# Render component
rendered_node = html(t"<{MyComponent} />", context=container)

# Collect assets from rendered HTML
collector.collect_from_node(rendered_node, location)
```

### 4. Path Rewriting

Transform relative paths to absolute URLs:

```python
html_string = str(rendered_node)

for asset in collector.assets:
    # Build absolute path
    absolute_url = f"/_static/{asset.module_path}"

    # Replace in HTML
    html_string = html_string.replace(
        f'"{asset.relative_path}"',
        f'"{absolute_url}"'
    )
```

## Supported Asset Types

The collector automatically detects:

- **Stylesheets**: `<link href="..." rel="stylesheet">`
- **Scripts**: `<script src="..."></script>`
- **Images**: `<img src="...">`
- **Other resources**: Any `src` or `href` attribute with relative paths

**Note**: External URLs (http://, https://) and special schemes (data:, blob:) are ignored.

## API Reference

### PathCollector Methods

#### `register_component(component_type: type) -> ComponentLocation`

Register a component and return its location.

**Returns:** `ComponentLocation` object for the component

**Example:**
```python
location = collector.register_component(Head)
```

#### `collect_from_node(node: Node, location: ComponentLocation) -> None`

Scan a rendered node for asset references.

**Parameters:**
- `node`: The rendered tdom Node
- `location`: ComponentLocation from `register_component()`

**Example:**
```python
collector.collect_from_node(rendered_html, location)
```

#### `clear() -> None`

Clear all registered components and collected assets.

**Example:**
```python
collector.clear()  # Reset for next render
```

### Properties

#### `assets: list[AssetReference]`

List of all collected asset references.

#### `components: dict[type, ComponentLocation]`

Dictionary mapping component types to their locations.

## Complete Example

See the path middleware example for a complete implementation:

{doc}`../examples/middleware/index` - Middleware examples including path collection

## Integration with Middleware

Path collection is typically used with middleware:

```python
@middleware
@dataclass
class PathMiddleware:
    """Middleware that collects paths during component rendering."""

    collector: Inject[PathCollector]
    priority: int = -100  # Run early

    def __call__(self, component, props, context):
        # Register component location
        location = self.collector.register_component(component)

        # Store location for post-render collection
        props['__path_location'] = location

        return props
```

## See Also

- {doc}`middleware` - Middleware system documentation
- {doc}`../examples/middleware/index` - Middleware examples
- {doc}`introspection` - Registry introspection for discovering components
