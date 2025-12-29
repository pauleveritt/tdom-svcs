# Middleware Examples

This directory contains examples demonstrating the middleware system in tdom-svcs.

## Overview

The middleware system provides pluggable hooks for logging, validation, transformation, and error handling during component lifecycle phases. Middleware executes in priority order before component resolution.

## Service Pattern (Recommended)

The recommended pattern treats **MiddlewareManager as a service**, enabling:
- Dependency injection for MiddlewareManager
- Consistent service lifecycle management
- Easy testing with fakes
- Integration with other services

## Examples

### 01_basic_middleware.py

**Basic middleware usage with service pattern**

Demonstrates:
- Setting up MiddlewareManager as a service (default behavior)
- Getting manager via dependency injection
- Registering middleware instances
- Priority-based execution order
- Halting execution when middleware returns None
- LoggingMiddleware, ValidationMiddleware, and TransformationMiddleware

Run:
```bash
uv run python examples/middleware/01_basic_middleware.py
```

### 02_middleware_with_dependencies.py

**Middleware with service dependencies**

Demonstrates:
- Middleware as services with their own dependencies
- Using `register_middleware_service()` for DI-constructed middleware
- Factory functions that use `svcs.Container`
- Different middleware implementations per environment

Run:
```bash
uv run python examples/middleware/02_middleware_with_dependencies.py
```

### 03_testing_with_fakes.py

**Testing middleware following svcs best practices**

Demonstrates:
- Creating simple fakes instead of mocks
- Registering fakes in test registry
- Testing middleware behavior in isolation
- Two patterns: with container and direct injection

Run:
```bash
uv run python examples/middleware/03_testing_with_fakes.py
```

### 04_manual_registration.py

**Manual registration without services**

Demonstrates:
- Creating MiddlewareManager directly (no DI)
- Registering middleware manually
- Using plain dict as context
- When to use this simpler pattern

Run:
```bash
uv run python examples/middleware/04_manual_registration.py
```

### 05_error_handling_middleware.py

**Error handling patterns**

Demonstrates:
- Catching and handling exceptions in middleware
- Wrapping component execution with try/except
- Fallback rendering on error
- Error recovery patterns
- Circuit breaker pattern for fail-fast behavior
- Priority-based error handling (early detection, late recovery)

Run:
```bash
uv run python examples/middleware/05_error_handling_middleware.py
```

### 06_global_and_per_component.py

**Global and per-component middleware (COMPREHENSIVE)**

This is the most complete example showing all middleware features together.

Demonstrates:
- Global middleware via MiddlewareManager (applies to all components)
- Per-component middleware via @component decorator
- Imperative register_component() as alternative to decorator
- Execution order: global middleware first, then per-component
- Priority ordering within each group (global, per-component)
- Both class components (Button, Card) and function components (Heading, Paragraph)
- Component type detection via isinstance(component, type)

Run:
```bash
uv run python examples/middleware/06_global_and_per_component.py
```

### 07_async_middleware.py

**Async middleware patterns**

Demonstrates:
- Async middleware with async __call__ method
- Mixed sync and async middleware in same chain
- Automatic async detection via inspect.iscoroutinefunction()
- Priority-based ordering maintained for async middleware
- Real-world async use cases:
  - Database queries (AsyncDatabaseMiddleware)
  - API calls (AsyncAPIMiddleware)
  - Remote validation (AsyncValidationMiddleware)
  - Async error handling (AsyncErrorHandlerMiddleware)
- Using await manager.execute_async()

Run:
```bash
uv run python examples/middleware/07_async_middleware.py
```

## Quick Start Guide

### 1. Basic Usage (Service Pattern)

```python
import svcs
from tdom_svcs.services.middleware import setup_container, MiddlewareManager
from dataclasses import dataclass

# Define middleware
@dataclass
class LoggingMiddleware:
    priority: int = 0

    def __call__(self, component, props, context):
        print(f"Processing {component.__name__}")
        return props  # Return props to continue, None to halt

# Setup
registry = svcs.Registry()
context = {"config": {}}
setup_container(context, registry)

# Get manager via DI and register middleware
container = svcs.Container(registry)
manager = container.get(MiddlewareManager)
manager.register_middleware(LoggingMiddleware())

# Execute middleware chain
props = {"title": "Click Me"}
result = manager.execute(Button, props, context)
```

### 2. Per-Component Middleware

```python
from tdom_svcs.services.middleware import component

# Using decorator
@component(middleware={
    "pre_resolution": [LoggingMiddleware(), ValidationMiddleware()]
})
@dataclass
class Button:
    title: str

# Or using imperative function
from tdom_svcs.services.middleware import register_component

@dataclass
class Card:
    title: str

register_component(Card, middleware={
    "pre_resolution": [LoggingMiddleware()]
})
```

### 3. Async Middleware

```python
@dataclass
class AsyncDatabaseMiddleware:
    priority: int = 0

    async def __call__(self, component, props, context):
        # Async operations
        data = await fetch_from_database()
        props["data"] = data
        return props

# Use with execute_async
result = await manager.execute_async(Component, props, context)
```

## Key Concepts

### Middleware Protocol

Middleware must satisfy the `Middleware` protocol:
```python
@dataclass
class MyMiddleware:
    priority: int = 0  # -100 to +100, lower executes first

    def __call__(self, component, props, context):
        # Modify props and return to continue
        props["added_field"] = "value"
        return props

        # Or return None to halt execution
        # return None
```

### Priority-Based Execution

- Range: -100 to +100
- Default: 0
- Lower numbers execute first
- Example: logging (-10), validation (0), transformation (10)

### Execution Order

When both global and per-component middleware are registered:

1. **Global Middleware** (via MiddlewareManager)
   - Executes in priority order: -10, 0, 10, etc.
   - Applies to all components

2. **Per-Component Middleware** (via @component)
   - Executes after global middleware
   - Also in priority order: -10, 0, 10, etc.
   - Only applies to specific component

Example execution flow:
```
Global (-10) -> Global (0) -> Global (10) ->
PerComponent (-5) -> PerComponent (0) -> PerComponent (5)
```

### Service Registration

Using `setup_container()` (recommended):
```python
import svcs
from tdom_svcs.services.middleware import setup_container, MiddlewareManager

registry = svcs.Registry()
context = {"config": {"debug": True}}

# Registers MiddlewareManager as service by default
setup_container(context, registry)

container = svcs.Container(registry)
manager = container.get(MiddlewareManager)  # Via DI!
```

### Middleware as Services

Register middleware with dependencies:
```python
def create_logging_middleware(container: svcs.Container) -> LoggingMiddleware:
    logger = container.get(Logger)
    return LoggingMiddleware(logger=logger)

registry.register_factory(LoggingMiddleware, create_logging_middleware)
manager.register_middleware_service(LoggingMiddleware, container)
```

### Context Protocol

Context is a dict-like interface:
```python
# Works with plain dict
context = {"logger": logger, "config": config}

# Works with svcs.Container
context = container

# Middleware accesses via dict-like interface
logger = context["logger"]
config = context.get("config", default_config)
```

### Component Type Detection

Middleware can detect whether it's processing a class or function component:

```python
def __call__(self, component, props, context):
    if isinstance(component, type):
        # Class component (Button, Card, etc.)
        print(f"Class: {component.__name__}")
    else:
        # Function component (heading, paragraph, etc.)
        print(f"Function: {component.__name__}")
    return props
```

## Testing Best Practices

Following svcs guidelines:

✅ **DO**:
- Create simple fakes that implement the protocol
- Register fakes in test registry
- Inject fakes directly when possible
- Test behavior, not implementation

❌ **DON'T**:
- Use mock frameworks unless necessary
- Create complex fakes with lots of state
- Test svcs container mechanics
- Mock the middleware under test

Example:
```python
@dataclass
class FakeLogger:
    _logs: list[str] = field(default_factory=list)

    def info(self, msg: str):
        self._logs.append(msg)

    def get_logs(self):
        return self._logs.copy()

# Use in tests
fake_logger = FakeLogger()
middleware = LoggingMiddleware(logger=fake_logger)
# ... execute middleware ...
assert len(fake_logger.get_logs()) == 1
```

## When to Use Each Pattern

### Use Service Pattern When:
- Your app already uses svcs for dependency injection
- Middleware need their own service dependencies
- You want consistent service lifecycle management
- You need different middleware per environment

### Use Manual Pattern When:
- Building simple scripts or prototypes
- No dependency injection needed
- Quick testing scenarios
- Minimal overhead is important

### Use Per-Component Middleware When:
- Specific components need unique middleware
- Different validation rules per component
- Component-specific logging or transformation
- Want to keep global middleware minimal

### Use Global Middleware When:
- Middleware applies to all components
- Cross-cutting concerns (logging, timing)
- Common validation or transformation
- Application-wide error handling

## Common Patterns

### 1. Logging Middleware
```python
@dataclass
class LoggingMiddleware:
    priority: int = -10  # Run early

    def __call__(self, component, props, context):
        name = component.__name__ if hasattr(component, "__name__") else str(component)
        print(f"Processing {name} with props: {props}")
        return props
```

### 2. Validation Middleware
```python
@dataclass
class ValidationMiddleware:
    priority: int = 0  # Default priority

    def __call__(self, component, props, context):
        if "required_field" not in props:
            print("Validation failed")
            return None  # Halt execution
        return props
```

### 3. Transformation Middleware
```python
@dataclass
class TransformationMiddleware:
    priority: int = 10  # Run late

    def __call__(self, component, props, context):
        props["timestamp"] = datetime.now().isoformat()
        props["normalized_title"] = props.get("title", "").lower()
        return props
```

### 4. Error Handling Middleware
```python
@dataclass
class ErrorHandlingMiddleware:
    priority: int = 100  # Run very late
    fallback_props: dict[str, Any] | None = None

    def __call__(self, component, props, context):
        try:
            # Validation logic
            if "invalid" in props:
                raise ValueError("Invalid props")
            return props
        except Exception as e:
            print(f"Error: {e}")
            return self.fallback_props or None
```

### 5. Async Database Middleware
```python
@dataclass
class AsyncDatabaseMiddleware:
    priority: int = -5

    async def __call__(self, component, props, context):
        # Fetch data asynchronously
        data = await database.query(props.get("id"))
        props["data"] = data
        return props
```

## Further Reading

- [services.md](../../agent-os/standards/global/services.md) - Service pattern guidelines
- [spec.md](../../agent-os/specs/2025-12-29-component-lifecycle-middleware-system/spec.md) - Full specification
- [svcs documentation](https://svcs.hynek.me/) - Service container details

## Example Execution Order

See examples for complete demonstrations, but here's the recommended order:

1. **01_basic_middleware.py** - Start here for basic concepts
2. **04_manual_registration.py** - Simple pattern without DI
3. **02_middleware_with_dependencies.py** - Service dependencies
4. **03_testing_with_fakes.py** - Testing patterns
5. **05_error_handling_middleware.py** - Error handling
6. **06_global_and_per_component.py** - Complete comprehensive example
7. **07_async_middleware.py** - Async patterns
