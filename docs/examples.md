# Examples

This page provides an overview of all working examples in the `examples/` directory. Each example is a complete, runnable Python script demonstrating specific features and patterns.

## Running Examples

All examples can be run directly with Python 3.14+:

```bash
# Using uv (recommended)
uv run python examples/example_name.py

# Using python directly
python examples/example_name.py
```

## Quick Links by Category

- [Basic Component Examples](#basic-component-examples)
- [Override Pattern Examples](#component-override-patterns)
- [Middleware Examples](#middleware-examples)
- [Advanced Integration Examples](#advanced-integration-examples)

## Basic Component Examples

### Pure tdom with Context

**File:** [examples/pure_tdom.py](../examples/pure_tdom.py)

The simplest possible example showing config and context as plain dictionaries with no svcs container or DI framework. Perfect for understanding the core concepts.

**Key concepts:**
- Config as a simple dataclass with component_lookup
- Context as a plain dictionary
- Components receiving and using context data
- How context flows from parent to child components
- No dependencies on svcs or DI framework

**When to use:**
- Learning tdom-svcs fundamentals
- Understanding context flow patterns
- Prototyping without framework overhead
- Teaching basic component concepts

**Example output:**
```text
<div class="dashboard">
  <header><div class='greeting'>Hello, Alice!</div></header>
  <main>
    <div class="user-info">
      <h2>Alice</h2>
      <p>Role: admin</p>
    </div>
  </main>
</div>
```

### Resource-Based Components

**File:** [examples/resource_based_components.py](../examples/resource_based_components.py)

Demonstrates how to register multiple implementations of a component for different resource contexts (e.g., customer types, tenants).

**Key concepts:**
- Using `@injectable(resource=...)` decorator
- Multi-implementation registration
- HopscotchInjector automatic selection
- Context-aware component resolution

**When to use:**
- Multi-tenant SaaS applications
- Different features per user tier
- Role-based UI customizations

### Location-Based Components

**File:** [examples/location_based_components.py](../examples/location_based_components.py)

Shows how to register components for specific URL paths, enabling path-specific layouts and behavior.

**Key concepts:**
- Using `@injectable(location=PurePath(...))` decorator
- Path hierarchy and matching
- URL-based component selection
- Fallback to base implementation

**When to use:**
- Different layouts per site section
- Path-specific authentication requirements
- Section-specific features

## Component Override Patterns

These examples demonstrate the three primary patterns for overriding component implementations.

### Global Override

**File:** [examples/override_global.py](../examples/override_global.py)

Demonstrates site-wide component customization by registering the same component name multiple times. The last registration wins globally.

**Key concepts:**
- Simple override pattern
- Last registration wins
- Site-wide customization
- Third-party component overrides

**When to use:**
- Customize base components for your site
- Override third-party library components
- Environment-specific implementations

**Example output:**
```text
Button type: <class 'ThemedButton'>
Rendered: <button style="color: #007bff">Submit</button>
```

### Resource-Based Override

**File:** [examples/override_resource.py](../examples/override_resource.py)

Shows multi-tenant component resolution with different implementations for customer types.

**Key concepts:**
- Multiple implementations per resource
- Resource context detection
- Tenant-specific customization
- Automatic implementation selection

**When to use:**
- Multi-tenant applications
- Tiered service offerings (free, premium, enterprise)
- Role-based UI variations

**Example output:**
```text
Customer Dashboard - Views: 100, Clicks: 50
Premium Dashboard - Views: 100, Clicks: 50, Conversions: 25, Revenue: $1000
Admin Dashboard - Full Access [System Controls Available]
```

### Location-Based Override

**File:** [examples/override_location.py](../examples/override_location.py)

Demonstrates URL path-based component selection with hierarchical path matching.

**Key concepts:**
- Path-based implementation selection
- Hierarchical path resolution
- Path-specific layouts
- Fallback to parent or root paths

**When to use:**
- Different layouts per site section
- Admin vs. public area separation
- Path-based authentication

**Example output:**
```text
Home Page Layout - Featured Content
Admin Layout - System Access Granted
Documentation Layout - Search, TOC, Navigation
```

## Middleware Examples

The `examples/middleware/` directory contains 7 comprehensive middleware examples:

### 01: Basic Middleware

**File:** [examples/middleware/01_basic_middleware.py](../examples/middleware/01_basic_middleware.py)

Introduction to middleware with logging, validation, and transformation examples.

**Key concepts:**
- Middleware protocol (`priority` + `__call__`)
- Execution order by priority
- Halting execution
- Prop transformation

**Middleware shown:**
- `LoggingMiddleware` - Observe component processing
- `ValidationMiddleware` - Validate props and halt if invalid
- `TransformationMiddleware` - Add timestamp and metadata

### 02: Middleware with Dependencies

**File:** [examples/middleware/02_middleware_with_dependencies.py](../examples/middleware/02_middleware_with_dependencies.py)

Shows how middleware can have injected dependencies from the service container.

**Key concepts:**
- Service-based middleware
- Dependency injection for middleware
- `register_middleware_service()` method
- Factory functions

**Middleware shown:**
- `LoggingMiddleware` with Logger service
- `MetricsMiddleware` with MetricsCollector service

### 03: Testing with Fakes

**File:** [examples/middleware/03_testing_with_fakes.py](../examples/middleware/03_testing_with_fakes.py)

Demonstrates testing patterns using fake/mock services following svcs best practices.

**Key concepts:**
- Creating fake services for tests
- Isolated middleware testing
- Component testing with fakes
- Test double patterns

**Testing patterns:**
- Test middleware in isolation
- Test components with fake services
- Integration testing

### 04: Manual Registration

**File:** [examples/middleware/04_manual_registration.py](../examples/middleware/04_manual_registration.py)

Shows manual MiddlewareManager registration without `setup_container()`.

**Key concepts:**
- Manual service registration
- Direct MiddlewareManager instantiation
- Alternative setup patterns

### 05: Error Handling Middleware

**File:** [examples/middleware/05_error_handling_middleware.py](../examples/middleware/05_error_handling_middleware.py)

Demonstrates error handling patterns and recovery strategies in middleware.

**Key concepts:**
- Try/except in middleware
- Error logging and recovery
- Graceful degradation
- Default value fallbacks

**Middleware shown:**
- `ErrorHandlingMiddleware` - Catch and log errors
- `FallbackMiddleware` - Provide defaults on error

### 06: Global and Per-Component Middleware

**File:** [examples/middleware/06_global_and_per_component.py](../examples/middleware/06_global_and_per_component.py)

Shows the difference between global middleware and per-component middleware registration.

**Key concepts:**
- Global middleware registration
- Per-component middleware
- Middleware scoping
- Execution order with mixed scopes

### 07: Async Middleware

**File:** [examples/middleware/07_async_middleware.py](../examples/middleware/07_async_middleware.py)

Demonstrates async middleware with automatic detection and mixed sync/async execution.

**Key concepts:**
- Async `__call__` methods
- Mixed sync and async middleware
- Automatic async detection
- `execute_async()` method

**Middleware shown:**
- `SyncLoggingMiddleware` - Synchronous logging
- `AsyncDatabaseMiddleware` - Async database queries
- `AsyncAPIMiddleware` - Async external API calls

## Advanced Integration Examples

### Full Application Setup

See {doc}`how_it_works` for complete application setup examples showing:
- Service registration
- Component scanning
- Infrastructure setup
- ComponentLookup integration

## Example Categories Summary

| Category | Count | Focus Area |
|----------|-------|------------|
| Basic Components | 3 | Component registration and resolution |
| Override Patterns | 3 | Component customization strategies |
| Middleware | 7 | Lifecycle hooks and cross-cutting concerns |
| **Total** | **13** | **Complete working examples** |

## Common Patterns Across Examples

### Setup Pattern

All examples follow a consistent setup pattern:

```python
def setup_application() -> svcs.Container:
    """Set up application with all services."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services
    registry.register_value(SomeService, SomeService())

    # Discover components
    scan_components(registry, component_registry, __name__)

    # Register infrastructure
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    return svcs.Container(registry)
```

### Component Pattern

All components use the class-based pattern with `@injectable`:

```python
@injectable
@dataclass
class MyComponent:
    """Component with dependencies and parameters."""

    service: Inject[SomeService]  # Injected
    param: str = "default"         # Regular parameter

    def __call__(self) -> str:
        """Render component."""
        data = self.service.get_data()
        return f"<div>{self.param}: {data}</div>"
```

### Middleware Pattern

All middleware follow the middleware protocol:

```python
@dataclass
class MyMiddleware:
    priority: int = 0  # Execution order

    def __call__(self, component, props, context):
        """Process props before component construction."""
        # Modify props, validate, add data, etc.
        return props  # Or None to halt
```

## Learning Path

We recommend exploring examples in this order:

1. **Start with fundamentals:**
   - `pure_tdom.py` - Understand config, context, and component basics
   - `resource_based_components.py` - Learn component registration with DI
   - `location_based_components.py` - Learn path-based resolution

2. **Learn override patterns:**
   - `override_global.py` - Simple site-wide customization
   - `override_resource.py` - Multi-tenant patterns
   - `override_location.py` - Path-based customization

3. **Master middleware:**
   - `middleware/01_basic_middleware.py` - Middleware fundamentals
   - `middleware/02_middleware_with_dependencies.py` - DI for middleware
   - `middleware/03_testing_with_fakes.py` - Testing patterns
   - `middleware/07_async_middleware.py` - Async support

4. **Advanced topics:**
   - Error handling patterns
   - Manual registration alternatives
   - Mixed middleware scopes

## Next Steps

After exploring examples:
- Read {doc}`how_it_works` for architectural deep dive
- Review {doc}`services/component_registry` for ComponentNameRegistry details
- Check {doc}`services/component_lookup` for resolution workflow
- Study {doc}`services/middleware` for middleware system details

## Contributing Examples

When adding new examples:
- Include comprehensive docstring at top
- Explain key concepts and use cases
- Provide runnable `if __name__ == "__main__"` block
- Follow established patterns (setup, component, middleware)
- Add to this documentation page
- Test with `uv run python examples/your_example.py`
