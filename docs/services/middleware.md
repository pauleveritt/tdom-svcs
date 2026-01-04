# MiddlewareManager Service

The **MiddlewareManager** service provides thread-safe middleware registration and execution for component lifecycle hooks. It enables cross-cutting concerns like logging, validation, transformation, and authorization across all components.

## Overview

Middleware are stateless callables that execute during component lifecycle phases. They can:
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

### Thread Safety

MiddlewareManager uses `threading.Lock` for thread-safe registration, making it safe for concurrent use in free-threaded Python 3.14+.

## Setup

### Creating an Instance

The recommended approach is to use `setup_container()` which automatically registers MiddlewareManager as a service:

```python
import svcs
from tdom_svcs.services.middleware import setup_container, MiddlewareManager

registry = svcs.Registry()
context = {"config": {"debug": True}}

# Registers MiddlewareManager as a service
setup_container(context, registry)

# Get manager via dependency injection
container = svcs.Container(registry)
manager = container.get(MiddlewareManager)
```

### Manual Registration

Alternatively, register MiddlewareManager manually:

```text
registry = svcs.Registry()
manager = MiddlewareManager()
registry.register_value(MiddlewareManager, manager)
```

## Middleware Registration

### Direct Instance Registration

Register middleware instances directly for simple cases:

```python
from dataclasses import dataclass
from tdom_svcs.services.middleware import MiddlewareManager

manager = MiddlewareManager()

@dataclass
class LoggingMiddleware:
    priority: int = -10

    def __call__(self, component, props, context):
        component_name = component.__name__ if hasattr(component, "__name__") else str(component)
        print(f"[LOG] Processing {component_name}")
        return props  # Continue execution

# Register the middleware instance
manager.register_middleware(LoggingMiddleware())
```

### Service-Based Registration

Register middleware as services for dependency injection:

```text
# Define middleware with dependencies
@dataclass
class DatabaseMiddleware:
    db: DatabaseService  # Injected dependency
    priority: int = -5

    def __call__(self, component, props, context):
        # Use database service
        data = self.db.query()
        props["_db_data"] = data
        return props

# Register as service
registry.register_factory(DatabaseService, create_database)
registry.register_factory(DatabaseMiddleware, DatabaseMiddleware)

# Register with MiddlewareManager
manager.register_middleware_service(DatabaseMiddleware, container)
```

## Execution Workflow

### Priority Ordering

Middleware execute in priority order (lower numbers first):

```python
from dataclasses import dataclass
from tdom_svcs.services.middleware import MiddlewareManager

manager = MiddlewareManager()

# Define a simple component for testing
class MyComponent:
    pass

@dataclass
class EarlyMiddleware:
    priority: int = -10  # Runs first

    def __call__(self, component, props, context):
        print("1. Early")
        return props

@dataclass
class MiddleMiddleware:
    priority: int = 0  # Runs second

    def __call__(self, component, props, context):
        print("2. Middle")
        return props

@dataclass
class LateMiddleware:
    priority: int = 10  # Runs third

    def __call__(self, component, props, context):
        print("3. Late")
        return props

manager.register_middleware(EarlyMiddleware())
manager.register_middleware(MiddleMiddleware())
manager.register_middleware(LateMiddleware())

# Execution prints: "1. Early", "2. Middle", "3. Late"
result = manager.execute(MyComponent, {}, {})
```

### Halting Execution

Middleware can halt the chain by returning `None`:

```python
from dataclasses import dataclass
from tdom_svcs.services.middleware import MiddlewareManager

manager = MiddlewareManager()

class MyComponent:
    pass

@dataclass
class ValidationMiddleware:
    priority: int = 0

    def __call__(self, component, props, context):
        if "required_field" not in props:
            print("[ERROR] Missing required field")
            return None  # Halt execution
        return props  # Continue

manager.register_middleware(ValidationMiddleware())

# Missing required field - execution halts
result = manager.execute(MyComponent, {}, {})
assert result is None  # Execution was halted
```

### Prop Transformation

Middleware can modify and pass props to the next middleware:

```python
from dataclasses import dataclass
from tdom_svcs.services.middleware import MiddlewareManager

manager = MiddlewareManager()

class MyComponent:
    pass

@dataclass
class EnrichmentMiddleware:
    priority: int = -10

    def __call__(self, component, props, context):
        # Add timestamp to props
        from datetime import datetime
        props["processed_at"] = datetime.now().isoformat()
        print(f"[ENRICH] Added timestamp: {props['processed_at']}")
        return props  # Pass modified props

@dataclass
class TransformMiddleware:
    priority: int = 0

    def __call__(self, component, props, context):
        # Transform existing prop
        if "title" in props:
            props["title"] = props["title"].upper()
            print(f"[TRANSFORM] Uppercased title: {props['title']}")
        return props

manager.register_middleware(EnrichmentMiddleware())
manager.register_middleware(TransformMiddleware())

# Execute with props
result = manager.execute(MyComponent, {"title": "hello"}, {})
assert result["title"] == "HELLO"
assert "processed_at" in result
```

## Async Support

### Async Middleware

Middleware with async `__call__` are automatically detected and awaited:

Example pattern from `examples/middleware/07_async_middleware.py`:

```text
@dataclass
class AsyncDatabaseMiddleware:
    """Async middleware that fetches data from database."""

    priority: int = -5

    async def __call__(self, component, props, context):
        """Fetch data from database asynchronously."""
        # Simulate async database query
        await asyncio.sleep(0.1)

        # Add fetched data to props
        props["_db_user"] = {"id": 123, "name": "John Doe"}
        return props
```

### Mixed Sync and Async

The middleware system supports mixing sync and async middleware:

```text
# Sync middleware
@dataclass
class SyncLoggingMiddleware:
    priority: int = -10

    def __call__(self, component, props, context):
        print("[SYNC] Logging")
        return props

# Async middleware
@dataclass
class AsyncAuthMiddleware:
    priority: int = 0

    async def __call__(self, component, props, context):
        # Async permission check
        await check_permissions()
        return props

# Use execute_async() for async middleware
result = await manager.execute_async(MyComponent, {}, {})
```

## Code Examples

Here are tested patterns extracted from the middleware examples:

### Basic Logging Middleware

From `examples/middleware/01_basic_middleware.py`:

```python
from dataclasses import dataclass
from tdom_svcs.services.middleware import MiddlewareManager

manager = MiddlewareManager()

@dataclass
class LoggingMiddleware:
    """Middleware that logs component processing."""

    priority: int = -10

    def __call__(self, component, props, context):
        component_name = component.__name__ if hasattr(component, "__name__") else str(component)
        print(f"[LOG] Processing {component_name} with props: {props}")
        return props

# Register and use
manager.register_middleware(LoggingMiddleware())

class Button:
    pass

result = manager.execute(Button, {"label": "Click"}, {})
assert result == {"label": "Click"}
```

### Validation Middleware

From `examples/middleware/01_basic_middleware.py`:

```python
from dataclasses import dataclass
from tdom_svcs.services.middleware import MiddlewareManager

manager = MiddlewareManager()

@dataclass
class ValidationMiddleware:
    """Middleware that validates props."""

    priority: int = 0

    def __call__(self, component, props, context):
        if "title" not in props:
            print("[VALIDATION] Error: 'title' field is required")
            return None  # Halt execution
        print(f"[VALIDATION] Props validated successfully")
        return props

# Register and use
manager.register_middleware(ValidationMiddleware())

class Card:
    pass

# Invalid props - returns None
result = manager.execute(Card, {"variant": "primary"}, {})
assert result is None

# Valid props - returns transformed props
result = manager.execute(Card, {"title": "Hello", "variant": "primary"}, {})
assert result == {"title": "Hello", "variant": "primary"}
```

### Transformation Middleware

From `examples/middleware/01_basic_middleware.py`:

```python
from dataclasses import dataclass
from datetime import datetime
from tdom_svcs.services.middleware import MiddlewareManager

manager = MiddlewareManager()

@dataclass
class TransformationMiddleware:
    """Middleware that transforms props."""

    priority: int = 10

    def __call__(self, component, props, context):
        props["processed_at"] = datetime.now().isoformat()
        print(f"[TRANSFORM] Added timestamp: {props['processed_at']}")
        return props

# Register and use
manager.register_middleware(TransformationMiddleware())

class Alert:
    pass

result = manager.execute(Alert, {"message": "Warning"}, {})
assert "processed_at" in result
assert "message" in result
```

## Complete Example

Here's a complete example combining multiple middleware:

```text
from dataclasses import dataclass
from datetime import datetime
import svcs
from tdom_svcs.services.middleware import MiddlewareManager, setup_container, Context
from typing import cast

# Define middleware
@dataclass
class LoggingMiddleware:
    priority: int = -10

    def __call__(self, component, props, context):
        name = component.__name__ if hasattr(component, "__name__") else str(component)
        print(f"[LOG] Processing {name}")
        return props

@dataclass
class ValidationMiddleware:
    priority: int = 0

    def __call__(self, component, props, context):
        if "title" not in props:
            return None  # Halt if invalid
        return props

@dataclass
class EnrichmentMiddleware:
    priority: int = 10

    def __call__(self, component, props, context):
        props["processed_at"] = datetime.now().isoformat()
        return props

# Setup application
registry = svcs.Registry()
context: Context = cast(Context, {"config": {"debug": True}})
setup_container(context, registry)

# Get manager and register middleware
container = svcs.Container(registry)
manager = container.get(MiddlewareManager)
manager.register_middleware(LoggingMiddleware())
manager.register_middleware(ValidationMiddleware())
manager.register_middleware(EnrichmentMiddleware())

# Use middleware
class Button:
    pass

# Valid execution
result = manager.execute(Button, {"title": "Click"}, context)
assert result is not None
assert "title" in result
assert "processed_at" in result

# Invalid execution (missing title)
result = manager.execute(Button, {}, context)
assert result is None  # Halted by validation
```

## Full Example Links

The `examples/middleware/` directory contains 7 complete working examples:

| Example | Description | Key Concepts |
|---------|-------------|--------------|
| [01_basic_middleware.py](../../examples/middleware/01_basic_middleware.py) | Basic middleware usage with service pattern | Setup, registration, execution |
| [02_middleware_with_dependencies.py](../../examples/middleware/02_middleware_with_dependencies.py) | Middleware with injected dependencies | Service-based registration, DI |
| [03_testing_with_fakes.py](../../examples/middleware/03_testing_with_fakes.py) | Testing middleware with mock services | Test doubles, isolation |
| [04_manual_registration.py](../../examples/middleware/04_manual_registration.py) | Manual MiddlewareManager registration | Direct instantiation |
| [05_error_handling_middleware.py](../../examples/middleware/05_error_handling_middleware.py) | Error handling and recovery patterns | Exception handling, fallbacks |
| [06_global_and_per_component.py](../../examples/middleware/06_global_and_per_component.py) | Global vs per-component middleware | Middleware scoping |
| [07_async_middleware.py](../../examples/middleware/07_async_middleware.py) | Async middleware with mixed sync/async | Async support, automatic detection |

## Best Practices

### 1. Use Appropriate Priorities

Organize middleware by priority based on dependencies:

```text
-10: Logging, metrics (observe but don't modify)
-5:  Authentication, authorization (early checks)
0:   Validation (check props are valid)
5:   Data enrichment (add contextual data)
10:  Transformation (final modifications)
```

### 2. Keep Middleware Stateless

Middleware should not maintain state between executions:

```python
# ✅ Good - stateless
@dataclass
class LoggingMiddleware:
    priority: int = -10

    def __call__(self, component, props, context):
        # Uses props and context, no instance state
        print(f"Processing: {props}")
        return props

# ❌ Bad - stateful (use service dependency instead)
@dataclass
class CountingMiddleware:
    priority: int = 0
    count: int = 0  # State that persists

    def __call__(self, component, props, context):
        self.count += 1  # Mutating state
        return props
```

### 3. Use Service-Based Registration for Dependencies

When middleware need dependencies, register them as services:

```text
# Middleware with dependencies
@dataclass
class AuthMiddleware:
    auth_service: AuthService  # Injected
    priority: int = -5

    def __call__(self, component, props, context):
        if not self.auth_service.check_permission():
            return None
        return props

# Register as service
registry.register_factory(AuthService, create_auth_service)
registry.register_factory(AuthMiddleware, AuthMiddleware)
manager.register_middleware_service(AuthMiddleware, container)
```

### 4. Fail Fast with Clear Messages

Provide helpful error messages when halting:

```python
@dataclass
class ValidationMiddleware:
    priority: int = 0

    def __call__(self, component, props, context):
        if "required_field" not in props:
            component_name = component.__name__ if hasattr(component, "__name__") else str(component)
            print(f"[ERROR] {component_name}: Missing required field 'required_field'")
            return None
        return props
```

## Error Handling

### TypeError: does not satisfy Middleware protocol

**Cause:** Object doesn't have required `priority` attribute or `__call__` method.

**Solution:** Ensure middleware has both requirements:

```python
@dataclass
class MyMiddleware:
    priority: int = 0  # Required

    def __call__(self, component, props, context):  # Required
        return props
```

### RuntimeError: Async middleware detected in synchronous execution

**Cause:** Using `execute()` with async middleware.

**Solution:** Use `execute_async()` instead:

```text
# ❌ Wrong
result = manager.execute(component, props, context)  # Fails if async middleware

# ✅ Correct
result = await manager.execute_async(component, props, context)
```

## See Also

- {doc}`../core_concepts` - Understand middleware concepts
- {doc}`../how_it_works` - Architecture and patterns
- {doc}`../examples` - More usage examples
- [Middleware Examples Directory](../../examples/middleware/) - Complete examples
