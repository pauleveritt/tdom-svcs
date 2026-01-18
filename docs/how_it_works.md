# How tdom-svcs Works

This document explains the core architecture, design decisions, and usage patterns for tdom-svcs.

## Overview

tdom-svcs integrates dependency injection (via `svcs` and `svcs-di`) with template-based component rendering (via `tdom`). It provides a bridge between string-based component names in templates and actual Python class implementations with automatic dependency resolution.

## Component Type Policy

### Class Components vs Function Components

tdom-svcs makes a clear distinction between class and function components:

#### ✅ Class Components (Recommended for Production)

**What they are:** Python classes (typically dataclasses) that can be instantiated with dependencies.

**What they can do:**
- Use `Inject[]` for automatic dependency injection
- Be discovered via `@injectable` decorator and `scan()`
- Be resolved directly from the container by type
- Be easily tested and composed

**Example:**
```python
from dataclasses import dataclass
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable

@injectable
@dataclass
class Button:
    """Button component with injected database service."""
    db: Inject[DatabaseService]  # Automatically injected
    label: str = "Click"  # Regular parameter with default

    def __call__(self) -> str:
        # Access injected dependency
        data = self.db.get_button_config()
        return f"<button>{self.label}</button>"
```

#### ✅ Function Components (Limited Use Cases)

**What they are:** Regular Python functions.

**What they can do:**
- Use `Inject[]` for automatic dependency injection when called directly
- Be called programmatically with dependencies resolved

**What they CANNOT do:**
- Be discovered via `@injectable` (svcs-di enforces this)
- Be registered in the container
- Be used in component composition patterns

**Example:**
```python
from svcs_di import Inject

def simple_widget(
    label: str,
    theme: Inject[ThemeService]  # Can use Inject[]
) -> str:
    color = theme.get_color()
    return f"<div style='color: {color}'>{label}</div>"

# Must be called directly with injector:
injector = KeywordInjector(container=container)
result = injector(simple_widget, label="Hello")
```

### Why This Distinction?

**Production-ready patterns:**
- Classes provide consistent interfaces for DI composition
- Type checkers understand `type[T]` generics better
- Classes can be easily composed and tested
- Functions are more flexible but less suitable for production

**Best practices:**
- Use class components with HopscotchInjector for production
- Register via `@injectable` decorator and `scan()`
- Resolve directly from container with `container.get(ComponentType)`

## Injector Usage Policy

tdom-svcs supports two types of injectors from `svcs-di`. Choose the right one for your use case:

### HopscotchContainer (Production - Use This)

**When to use:**
- Production applications
- Multi-tenant or context-aware applications
- Any time you need resource or location-based resolution

**Capabilities:**
- ✅ Built-in `inject()` method with automatic dependency injection
- ✅ Resource-based resolution (`resource=CustomerContext`)
- ✅ Location-based resolution (`location=PurePath("/admin")`)
- ✅ Multi-implementation support
- ✅ Async component support via `ainject()`

**Example:**
```python
from svcs_di import HopscotchContainer, HopscotchRegistry

# Create registry and container
registry = HopscotchRegistry()
registry.register_value(DatabaseService, DatabaseService())

# Use HopscotchContainer with built-in inject()
with HopscotchContainer(registry) as container:
    # Resolve components with automatic dependency injection
    button = container.inject(Button)

    # With resource-based resolution
    dashboard = container.inject(Dashboard, resource=CustomerContext)
```

### KeywordInjector (Educational Only)

**When to use:**
- Simple educational examples
- Function components
- Demonstrating basic `Inject[]` concept

**Limitations:**
- ❌ No resource-based resolution
- ❌ No location-based resolution
- ❌ Not suitable for class components in production
- ❌ Cannot be used with container.get()

**Example (educational only):**
```python
from svcs_di.injectors.keyword import KeywordInjector

# Simple function with Inject[]
def greet(name: str, formatter: Inject[FormatService]) -> str:
    return formatter.format(f"Hello, {name}")

# Direct call with KeywordInjector
injector = KeywordInjector(container=container)
result = injector(greet, name="World")
```

**Important:** Use HopscotchInjector for production applications with class components.

## Type Hinting Approach

tdom-svcs uses modern Python type hinting with generics for type safety and IDE support.

### Generic Type Parameters

**Problem we solved:** Type checkers need `type[T]` (generic) not `type` (base metaclass).

**Solution:** Use TypeVar and generic parameters throughout:

```python
from typing import TypeVar

T = TypeVar("T")

def _construct_sync_component(self, component_type: type[T]) -> T:
    """Construct a component and preserve its type."""
    injector = self.container.get(HopscotchInjector)
    return injector(component_type)  # Type checker knows: type[T] → T
```

**Benefits:**
- ✅ IDE autocomplete knows exact component types
- ✅ Type checker validates correct usage
- ✅ No `cast()` calls needed - proper types from start
- ✅ Fail fast with clear error messages

### Validation at Registration Time

**Early validation is better than late failure:**

Components are validated when registered during application setup. This ensures errors are caught early rather than during request handling.

**Benefits:**
- Errors happen at startup (setup time), not at runtime (request time)
- Clear, actionable error messages from the container
- Type checker can reason about component types correctly

## Core Architecture



### scan()

**Purpose:** Automatically discover `@injectable` decorated classes and register them.

**How it works:**
1. Scan specified packages for modules
2. Find classes decorated with `@injectable`
3. Extract metadata (resource, location, etc.)
4. Register in svcs.Registry
5. Validate all items are classes (skip non-classes with warning)

**Usage:**
```python
from svcs_di.injectors.locator import scan

# Scan packages for components
scan(
    registry,              # svcs.Registry
    "app.components",      # Package to scan
)
scan(
    registry,
    "app.widgets",         # Another package
)

# Now all @injectable components are registered automatically
```

**Example structure:**
```
app/
├── components/
│   ├── __init__.py
│   ├── button.py       # @injectable Button class
│   └── card.py         # @injectable Card class
└── widgets/
    ├── __init__.py
    └── chart.py        # @injectable Chart class
```

## Dependency Injection with Inject[]

### Basic Usage

Mark dependencies that should be injected from the container:

```python
from dataclasses import dataclass
from svcs_di import Inject

@dataclass
class UserProfile:
    db: Inject[DatabaseService]     # Injected from container
    cache: Inject[CacheService]     # Injected from container
    user_id: int                     # Regular parameter (from context)

    def __call__(self) -> str:
        # Access injected dependencies
        user = self.db.get_user(self.user_id)
        cached = self.cache.get(f"user_{self.user_id}")
        return f"<div>{user['name']}</div>"
```

### Field Order in Dataclasses

**Important:** Fields without defaults must come before fields with defaults.

```python
# ❌ Wrong - SyntaxError
@dataclass
class MyComponent:
    name: str = "default"      # Has default
    db: Inject[DatabaseService] # No default - ERROR!

# ✅ Correct
@dataclass
class MyComponent:
    db: Inject[DatabaseService]  # No default first
    name: str = "default"        # Default second
```

### Mixing Injected and Regular Parameters

```python
@dataclass
class Button:
    db: Inject[DatabaseService]  # Injected from container
    label: str = "Click"         # Provided from context or default
    disabled: bool = False       # Provided from context or default

    def __call__(self) -> str:
        config = self.db.get_button_config()
        disabled_attr = " disabled" if self.disabled else ""
        return f"<button{disabled_attr}>{self.label}</button>"

# When resolving:
button = lookup("Button", context={"label": "Submit", "disabled": True})
# - db: automatically injected from container
# - label: provided from context ("Submit")
# - disabled: provided from context (True)
```

## Advanced Features

### Resource-Based Resolution

Register multiple implementations of a component for different contexts:

```python
from pathlib import PurePath
from svcs_di.injectors.decorators import injectable

# Customer context
class CustomerContext:
    pass

# Admin context
class AdminContext:
    pass

@injectable(resource=CustomerContext)
@dataclass
class CustomerDashboard:
    """Dashboard for customers."""
    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        return "<div>Customer Dashboard</div>"

@injectable(resource=AdminContext)
@dataclass
class AdminDashboard:
    """Dashboard for admins."""
    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        return "<div>Admin Dashboard</div>"

# Resolution happens based on context
# HopscotchInjector selects correct implementation
```

See [examples/override_resource.py](../examples/override_resource.py) for a complete working example.

### Location-Based Resolution

Register components for specific URL paths:

```python
from pathlib import PurePath

@injectable(location=PurePath("/"))
@dataclass
class HomePage:
    """Home page component."""
    content: Inject[ContentService]

    def __call__(self) -> str:
        return "<div>Home Page</div>"

@injectable(location=PurePath("/admin"))
@dataclass
class AdminPanel:
    """Admin panel component."""
    auth: Inject[AuthService]

    def __call__(self) -> str:
        if not self.auth.is_admin():
            return "<div>Access Denied</div>"
        return "<div>Admin Panel</div>"

# HopscotchInjector resolves based on current location
```

See [examples/override_location.py](../examples/override_location.py) for a complete working example.

### Async Components

Components with async `__call__` methods are automatically detected:

```python
@injectable
@dataclass
class AsyncAlert:
    message: str = "Alert"

    async def __call__(self) -> str:
        """Async rendering."""
        return f"<div>{self.message}</div>"

# Container resolves async components - can await construction
component = await container.get(AsyncAlert)
output = await component()  # If component() is also async
```

## Middleware System

The **MiddlewareManager** service enables lifecycle hooks for components. Middleware can modify props, validate data, add context, log usage, or halt execution.

### What is Middleware?

Middleware are stateless callables that execute during component resolution. They provide a clean way to handle cross-cutting concerns without cluttering component logic.

**Common use cases:**
- Logging component usage
- Validating props before component construction
- Adding authentication/authorization checks
- Enriching props with contextual data
- Error handling and recovery

### Basic Middleware Pattern

```text
from dataclasses import dataclass
from tdom_svcs.services.middleware import MiddlewareManager

@dataclass
class LoggingMiddleware:
    priority: int = -10  # Lower numbers execute first

    def __call__(self, component, props, context):
        # Log component processing
        print(f"Processing {component.__name__}")
        return props  # Continue to next middleware

# Register middleware
manager = MiddlewareManager()
manager.register_middleware(LoggingMiddleware())

# Execute middleware chain
result = manager.execute(Button, {"label": "Click"}, {})
```

### Middleware Execution Order

Middleware execute in priority order:
- **-10:** Logging, metrics (observe but don't modify)
- **-5:** Authentication, authorization
- **0:** Validation (check requirements)
- **5:** Data enrichment (add context)
- **10:** Transformation (final modifications)

### Halting Execution

Middleware can halt the chain by returning `None`:

```text
@dataclass
class ValidationMiddleware:
    priority: int = 0

    def __call__(self, component, props, context):
        if "required_field" not in props:
            print("Validation failed")
            return None  # Halt - no more middleware runs
        return props  # Continue
```

### Async Middleware Support

Middleware with async `__call__` are automatically detected:

```text
@dataclass
class AsyncAuthMiddleware:
    priority: int = -5

    async def __call__(self, component, props, context):
        # Async permission check
        await check_user_permissions()
        return props

# Use execute_async() for async middleware
result = await manager.execute_async(Button, props, context)
```

For complete documentation and working examples, see {doc}`services/middleware`.

## Component Override Patterns

tdom-svcs supports three patterns for overriding component implementations: global overrides, resource-based overrides, and location-based overrides.

### Global Override Pattern

Override a component everywhere in your application by registering the custom implementation. The most recently registered version is used when resolving by type:

```python
# Base component
@injectable
@dataclass
class Button:
    label: str = "Click"

    def __call__(self) -> str:
        return f"<button>{self.label}</button>"

# Site-specific override
@injectable
@dataclass
class CustomButton(Button):  # Inherit interface
    theme: Inject[ThemeService]

    def __call__(self) -> str:
        color = self.theme.get_brand_color()
        return f"<button style='color: {color}'>{self.label}</button>"

# Register the custom implementation
registry.register_value(Button, CustomButton)
```

See [examples/override_global.py](../examples/override_global.py) for a complete working example showing how to override components at the site level.

### Resource-Based Override Pattern

Use different implementations based on the current resource context (e.g., customer type, tenant):

```text
# Base implementation
@injectable
@dataclass
class Dashboard:
    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        return "<div>Generic Dashboard</div>"

# Customer-specific implementation
@injectable(resource=CustomerContext)
@dataclass
class CustomerDashboard:
    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        return "<div>Customer Dashboard with Limited Features</div>"

# Admin-specific implementation
@injectable(resource=AdminContext)
@dataclass
class AdminDashboard:
    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        return "<div>Admin Dashboard with Full Access</div>"

# HopscotchInjector selects implementation based on resource context
```

**Override precedence:** HopscotchInjector selects the most specific match:
1. Exact resource match (e.g., `CustomerContext`)
2. Base implementation with no resource
3. Raises error if no match found

See [examples/override_resource.py](../examples/override_resource.py) for a complete working example of multi-tenancy with resource-based component resolution.

### Location-Based Override Pattern

Use different implementations based on URL path or location:

```text
# Base page component
@injectable
@dataclass
class PageLayout:
    content: Inject[ContentService]

    def __call__(self) -> str:
        return "<div>Standard Page Layout</div>"

# Admin area override
@injectable(location=PurePath("/admin"))
@dataclass
class AdminPageLayout:
    content: Inject[ContentService]
    auth: Inject[AuthService]

    def __call__(self) -> str:
        if not self.auth.is_admin():
            return "<div>Access Denied</div>"
        return "<div>Admin Page Layout</div>"

# HopscotchInjector selects implementation based on current location
```

**Override precedence:** HopscotchInjector matches the most specific path:
1. Exact location match (e.g., `/admin/users`)
2. Parent location match (e.g., `/admin`)
3. Root location match (e.g., `/`)
4. Base implementation with no location

See [examples/override_location.py](../examples/override_location.py) for a complete working example of URL path-based component resolution.

## Testing Patterns

tdom-svcs follows svcs best practices for testing with fake/mock services.

### Testing with Fakes

Use `registry.register_value()` to provide test doubles:

```text
from svcs_di import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.locator import scan

def test_button_with_fake_database():
    """Test component with a fake database service."""

    # Create fake service
    class FakeDatabaseService:
        def get_button_config(self):
            return {"color": "red", "size": "large"}

    # Setup container with fake
    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, FakeDatabaseService())

    # Scan components
    scan(registry, __name__)

    # Test with fake using inject()
    with HopscotchContainer(registry) as container:
        button = container.inject(Button)
        output = button()

    assert "red" in output or "Test" in output
```

### Testing Middleware

Test middleware in isolation by calling it directly:

```text
def test_validation_middleware():
    """Test validation middleware in isolation."""

    @dataclass
    class ValidationMiddleware:
        priority: int = 0

        def __call__(self, component, props, context):
            if "required_field" not in props:
                return None  # Halt
            return props  # Continue

    middleware = ValidationMiddleware()

    # Test with valid props
    result = middleware(Button, {"required_field": "value"}, {})
    assert result is not None
    assert result["required_field"] == "value"

    # Test with invalid props
    result = middleware(Button, {}, {})
    assert result is None  # Execution halted
```

### Testing Components

Test components with injected dependencies using fakes:

```text
from svcs_di import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.locator import scan

def test_user_profile_component():
    """Test component with multiple injected dependencies."""

    # Create fakes
    class FakeDatabase:
        def get_user(self, user_id):
            return {"name": "Test User", "email": "test@example.com"}

    class FakeCache:
        def get(self, key):
            return None

    # Setup container with fakes
    registry = HopscotchRegistry()
    registry.register_value(DatabaseService, FakeDatabase())
    registry.register_value(CacheService, FakeCache())

    # Scan for components
    scan(registry, __name__)

    # Test the component with inject()
    with HopscotchContainer(registry) as container:
        component = container.inject(UserProfile)
        # ... test assertions
```

### Integration Testing

Test end-to-end component resolution:

```text
from svcs_di import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.locator import scan

def test_component_resolution_integration():
    """Integration test for complete component resolution flow."""

    # Setup real services (or fakes)
    registry = HopscotchRegistry()

    # Register all services
    registry.register_value(DatabaseService, DatabaseService())
    registry.register_value(ThemeService, ThemeService())

    # Scan components
    scan(registry, "myapp.components")

    # Test resolution with inject()
    with HopscotchContainer(registry) as container:
        button = container.inject(Button)
        output = button()

    assert "Submit" in output or "<button" in output
```

For complete testing examples, see [examples/middleware/03_testing_with_fakes.py](../examples/middleware/03_testing_with_fakes.py).

## Complete Setup Example

Here's a complete application setup showing all the pieces together:

For more examples, see {doc}`examples` and the `examples/` directory in the repository.
