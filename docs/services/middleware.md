# Middleware

The **middleware system** provides registration and execution of middleware for component lifecycle hooks. It enables cross-cutting concerns like logging, validation, transformation, and authorization across components.

## Overview

Middleware are callables that execute during component lifecycle phases. They can:
- Modify component props before resolution
- Add contextual data (user info, permissions, etc.)
- Validate props and halt execution
- Log component usage and errors
- Transform data for components

### Purpose and Use Cases

**When to use middleware:**
- **Logging:** Track component usage and performance
- **Validation:** Ensure props meet requirements
- **Authorization:** Check user permissions
- **Data enrichment:** Add contextual data to props
- **Error handling:** Catch and handle errors uniformly
- **Metrics:** Collect usage statistics

Middleware provides a clean separation between component logic and cross-cutting concerns.

### Component Middleware for Node Trees

Beyond simple prop transformation, middleware is particularly powerful for **operating on the component node tree**:

- **Static path rewriting:** Transform asset paths (images, CSS, JS) based on deployment environment or CDN configuration
- **Link validation:** Check that internal links point to valid routes
- **i18n injection:** Add translation context or transform text nodes
- **Security scanning:** Detect potentially unsafe content before rendering
- **Tree optimization:** Remove unnecessary wrapper elements or flatten structures
- **Accessibility enhancement:** Add ARIA attributes or validate accessibility requirements

Component middleware receives the full container context, enabling rich transformations based on application state.

### Container Access: Read and Write

Middleware receives the DI container as the `context` parameter. This provides **both read and write access**:

**Reading from container:**
```python
def __call__(self, component, props, context):
    # Read services from container
    config = context.get(AppConfig)
    user = context.get(CurrentUser)
    return props
```

**Writing to container:**
```python
def __call__(self, component, props, context):
    # Write values for later middleware or components to use
    context.register_local_value(ProcessedData, {"computed": True})
    return props
```

This enables middleware to prepare data that subsequent middleware or components can consume, creating a powerful pipeline for request processing.

### Thread Safety

Middleware state is stored in `HopscotchRegistry.metadata()`, which uses thread-safe access patterns suitable for concurrent use in free-threaded Python 3.14+.

## Hopscotch Integration

The middleware system integrates seamlessly with Hopscotch's registry and container system. The `scan()` function automatically discovers and registers middleware:

```python
from svcs_di.injectors import HopscotchRegistry, HopscotchContainer
from tdom_svcs import scan, execute_middleware

# Create registry and scan packages
registry = HopscotchRegistry()
scan(registry, "myapp.services", "myapp.middleware", "myapp.components")

# Use container for middleware execution
with HopscotchContainer(registry) as container:
    result = execute_middleware(MyComponent, props, container)
```

The `scan()` function:
1. Calls `svcs_di`'s scan for `@injectable` services
2. Discovers `@middleware` decorated classes (global middleware)
3. Discovers `@component` decorated classes (per-component middleware)
4. Registers all discovered items with the registry

No manual `setup_container()` call is needed—`scan()` handles all registration automatically.

## Global vs Per-Component Middleware

The middleware system provides two distinct mechanisms:

### Global Middleware (Declared)

Middleware marked with `@middleware` are **global**—they run for **all components**:

```python
@middleware
@dataclass
class LoggingMiddleware:
    priority: int = -10

    def __call__(self, component, props, context):
        # Runs for EVERY component
        return props
```

Key points:
- The `@middleware` decorator registers the class for discovery by `scan()`
- Global middleware cannot be filtered by component type
- All global middleware runs via `execute_middleware()`, regardless of which component is being processed

### Per-Component Middleware (Opt-in)

Components can opt-in to **additional** middleware using `@component`. This middleware does **not** need the `@middleware` decorator, but must be `@injectable` for container resolution:

```python
from svcs_di.injectors import injectable

# No @middleware decorator needed, but @injectable is required
@injectable
@dataclass
class ButtonStyleMiddleware:
    priority: int = 0

    def __call__(self, component, props, context):
        props["styled"] = True
        return props

# Pass the TYPE, not an instance - container resolves it
@component(middleware={"pre_resolution": [ButtonStyleMiddleware]})
@dataclass
class Button:
    ...
```

Key points:
- Per-component middleware is **additive**—it runs in addition to global middleware, not instead of it
- The middleware class must be `@injectable` for container resolution
- Pass middleware **types** (not instances) to `@component`—the container manages lifecycle
- Per-component middleware is executed via `execute_component_middleware()`

### Execution Order

When processing a component:

1. **Global middleware** runs first (via `execute_middleware()`)
2. **Per-component middleware** runs after (via `execute_component_middleware()`)

```python
# Step 1: Global middleware
result = execute_middleware(Button, props, container)

# Step 2: Per-component middleware (resolves types from container)
result = execute_component_middleware(Button, result, container, "pre_resolution")
```

## Defining Middleware

### Using the @middleware Decorator

Mark middleware classes with the `@middleware` decorator for automatic discovery:

```python
from dataclasses import dataclass
from tdom_svcs import middleware

@middleware
@dataclass
class LoggingMiddleware:
    """Middleware that logs component processing."""

    priority: int = -10

    def __call__(self, component, props, context):
        component_name = getattr(component, "__name__", str(component))
        print(f"[LOG] Processing {component_name}")
        return props
```

The `@middleware` decorator:
- Marks the class for discovery by `scan()` as global middleware
- Automatically applies `@injectable` so it can be resolved from the DI container

Middleware must have:
- A `priority` attribute (int) - lower numbers run first
- A `__call__` method with signature `(component, props, context) -> props | None`

### Imperative Registration

For programmatic control, register middleware directly:

```python
from tdom_svcs import register_middleware

# Register middleware type with registry
register_middleware(registry, LoggingMiddleware)
```

This is useful when middleware needs to be registered conditionally or when not using scanning.

## Per-Component Middleware

### Using the @component Decorator

Apply middleware to specific components using the `@component` decorator:

```python
from dataclasses import dataclass
from svcs_di.injectors import injectable
from tdom_svcs import component

@injectable  # Required for container resolution
@dataclass
class ButtonStyleMiddleware:
    priority: int = 0

    def __call__(self, component, props, context):
        if "variant" not in props:
            props["variant"] = "primary"
        return props

# Pass the TYPE, not an instance
@component(middleware={"pre_resolution": [ButtonStyleMiddleware]})
@dataclass
class Button:
    label: str = "Click"
    variant: str = "default"
```

The `@component` decorator:
- Marks the class with per-component middleware configuration
- Automatically applies `@injectable` so it can be resolved from the DI container
- Middleware types are resolved from the container when executed

(middleware:lifecycle-phases)=
### Lifecycle Phases

Per-component middleware can target specific lifecycle phases:

- **`pre_resolution`**: Before component dependencies are resolved
- **`post_resolution`**: After dependencies resolved, before rendering
- **`rendering`**: During the rendering phase

```python
@component(middleware={
    "pre_resolution": [validation_mw],
    "post_resolution": [enrichment_mw],
    "rendering": [transform_mw],
})
class MyComponent:
    ...
```

### Retrieving Component Middleware

Access registered per-component middleware programmatically:

```python
from tdom_svcs import get_component_middleware

# Get middleware map for a component
mw_map = get_component_middleware(registry, Button)
pre_mw = mw_map.get("pre_resolution", [])

# Execute manually if needed
for mw in sorted(pre_mw, key=lambda m: m.priority):
    props = mw(Button, props, context)
```

## Execution

### Priority Ordering

Middleware execute in priority order (lower numbers first):

```python
@middleware
@dataclass
class EarlyMiddleware:
    priority: int = -10  # Runs first

@middleware
@dataclass
class MiddleMiddleware:
    priority: int = 0    # Runs second

@middleware
@dataclass
class LateMiddleware:
    priority: int = 10   # Runs third
```

Recommended priority ranges:
- `-10`: Logging, metrics (observe but don't modify)
- `-5`: Authentication, authorization (early checks)
- `0`: Validation (check props are valid)
- `5`: Data enrichment (add contextual data)
- `10`: Transformation (final modifications)

### Halting Execution

Middleware can halt the chain by returning `None`:

```python
@middleware
@dataclass
class ValidationMiddleware:
    priority: int = 0

    def __call__(self, component, props, context):
        if "required_field" not in props:
            print("[ERROR] Missing required field")
            return None  # Halt execution
        return props  # Continue
```

### Executing Middleware

Use `execute_middleware()` to run the middleware chain:

```python
from tdom_svcs import execute_middleware

with HopscotchContainer(registry) as container:
    result = execute_middleware(MyComponent, {"title": "Hello"}, container)

    if result is None:
        print("Middleware halted execution")
    else:
        print(f"Final props: {result}")
```

## Async Support

### Async Middleware

Define async middleware with an async `__call__` method:

```python
@middleware
@dataclass
class AsyncDatabaseMiddleware:
    priority: int = -5

    async def __call__(self, component, props, context):
        # Async database query
        user = await fetch_user(props.get("user_id"))
        props["_user"] = user
        return props
```

### Mixed Sync and Async

Use `execute_middleware_async()` when any middleware might be async:

```python
from tdom_svcs import execute_middleware_async

async def render():
    with HopscotchContainer(registry) as container:
        # Handles both sync and async middleware
        result = await execute_middleware_async(MyComponent, props, container)
```

Sync middleware in an async chain are called normally; async middleware are awaited automatically.

## Middleware with Dependencies

Middleware can have their own dependencies injected via factory functions:

```python
from dataclasses import dataclass
import svcs

@dataclass
class Logger:
    name: str

@middleware
@dataclass
class LoggingMiddleware:
    logger: Logger
    priority: int = -10

    def __call__(self, component, props, context):
        self.logger.info(f"Processing {component.__name__}")
        return props

# Register with factory function
def create_logging_middleware(container: svcs.Container) -> LoggingMiddleware:
    return LoggingMiddleware(logger=container.get(Logger))

registry.register_value(Logger, Logger(name="APP"))
registry.register_factory(LoggingMiddleware, create_logging_middleware)
register_middleware(registry, LoggingMiddleware)
```

## Complete Example

Here's a complete example showing the recommended patterns:

```python
from dataclasses import dataclass
from svcs_di.injectors import HopscotchRegistry, HopscotchContainer, injectable
from tdom_svcs import (
    middleware,
    component,
    scan,
    execute_middleware,
    execute_component_middleware,
)

# Global middleware with @middleware decorator
@middleware
@dataclass
class LoggingMiddleware:
    priority: int = -10

    def __call__(self, component, props, context):
        name = getattr(component, "__name__", str(component))
        print(f"[LOG] Processing {name}")
        return props

@middleware
@dataclass
class ValidationMiddleware:
    priority: int = 0

    def __call__(self, component, props, context):
        if "title" not in props:
            return None
        return props

# Per-component middleware (must be @injectable for container resolution)
@injectable
@dataclass
class ButtonStyleMiddleware:
    priority: int = 5

    def __call__(self, component, props, context):
        props["styled"] = True
        return props

# Pass the TYPE, not an instance
@component(middleware={"pre_resolution": [ButtonStyleMiddleware]})
@dataclass
class Button:
    title: str = ""
    styled: bool = False

# Application setup
registry = HopscotchRegistry()

# Register middleware as services
registry.register_value(LoggingMiddleware, LoggingMiddleware())
registry.register_value(ValidationMiddleware, ValidationMiddleware())

# Scan discovers @middleware and @component decorators
scan(registry, locals_dict=locals())

# Execute
with HopscotchContainer(registry) as container:
    # Global middleware runs first
    result = execute_middleware(Button, {"title": "Click"}, container)

    if result:
        # Then per-component middleware (resolves types from container)
        result = execute_component_middleware(Button, result, container, "pre_resolution")

        print(f"Final: {result}")  # {'title': 'Click', 'styled': True}
```

## Error Handling

### RuntimeError: Async middleware detected in synchronous execution

**Cause:** Using `execute_middleware()` with async middleware.

**Solution:** Use `execute_middleware_async()` instead:

```python
# Wrong - fails with async middleware
result = execute_middleware(component, props, container)

# Correct
result = await execute_middleware_async(component, props, container)
```

## See Also

- {doc}`../core_concepts` - Understand middleware concepts
- {doc}`../how_it_works` - Architecture and patterns
- {doc}`../examples/middleware/index` - Complete middleware examples
