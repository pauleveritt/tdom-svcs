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
- Be registered by string name in ComponentNameRegistry
- Be discovered via `@injectable` decorator and `scan_components()`
- Be resolved via ComponentLookup by string name
- Be referenced in templates (e.g., `<Button label="Click">`)

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
- Be registered by string name
- Be discovered via `@injectable` (svcs-di enforces this)
- Be resolved via ComponentLookup
- Be referenced in templates

**Example:**
```python
from svcs_di import Inject

def simple_widget(
    label: str,
    theme: Inject[ThemeService]  # Can use Inject[]
) -> str:
    color = theme.get_color()
    return f"<div style='color: {color}'>{label}</div>"

# Must be called directly, cannot use ComponentLookup:
injector = KeywordInjector(container=container)
result = injector(simple_widget, label="Hello")
```

### Why This Distinction?

**String name lookup requires classes:**
- Templates reference components by name: `<Button>`
- ComponentNameRegistry maps strings to types
- Only classes can be reliably registered and discovered
- Functions lack metadata needed for advanced resolution

**Type safety:**
- `ComponentNameRegistry` only accepts `type` (not `Callable`)
- Enforced at registration time with clear error messages
- Type checker understands `type[T]` generics throughout

## Injector Usage Policy

tdom-svcs supports two types of injectors from `svcs-di`. Choose the right one for your use case:

### HopscotchInjector (Production - Use This)

**When to use:**
- Class components with ComponentLookup
- Production applications
- Multi-tenant or context-aware applications
- Any time you need resource or location-based resolution

**Capabilities:**
- ✅ Resource-based resolution (`resource=CustomerContext`)
- ✅ Location-based resolution (`location=PurePath("/admin")`)
- ✅ Multi-implementation support
- ✅ Full ComponentLookup integration
- ✅ Async component support via `HopscotchAsyncInjector`

**Example:**
```python
from svcs_di.injectors.locator import HopscotchInjector, HopscotchAsyncInjector

# Register the production injector
registry.register_factory(HopscotchInjector, HopscotchInjector)
registry.register_factory(HopscotchAsyncInjector, HopscotchAsyncInjector)

# Use with ComponentLookup
lookup = ComponentLookup(container=container)
button = lookup("Button", context={"label": "Submit"})
```

### KeywordInjector (Educational Only)

**When to use:**
- Simple educational examples
- Function components without ComponentLookup
- Demonstrating basic `Inject[]` concept

**Limitations:**
- ❌ No resource-based resolution
- ❌ No location-based resolution
- ❌ No ComponentLookup integration
- ❌ Cannot resolve components by string name

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

**Important:** Do not use KeywordInjector with ComponentLookup or class components in production code.

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

```python
def register(self, name: str, component_type: type) -> None:
    """Register a component class type."""
    # Validate immediately - fail fast
    if not isinstance(component_type, type):
        raise TypeError(
            f"ComponentNameRegistry only accepts class types, "
            f"got {type(component_type).__name__}. "
            f"Function components cannot be registered by string name."
        )

    self._registry[name] = component_type
```

**Why this matters:**
- Errors happen at registration (setup time), not lookup (request time)
- Clear, actionable error messages
- Type checker can reason about types after validation

## Core Architecture

### ComponentNameRegistry

**Purpose:** Maps string names to component class types.

**Key features:**
- Thread-safe with locking
- Class-only registration (validated)
- Simple dictionary-based lookup
- Returns `type` or `None`

**Usage:**
```python
registry = ComponentNameRegistry()

# Register components by name
registry.register("Button", Button)
registry.register("Card", Card)

# Retrieve component types
button_class = registry.get_type("Button")  # Returns: type[Button]
unknown = registry.get_type("Unknown")  # Returns: None

# List all registered names
all_names = registry.get_all_names()  # Returns: ["Button", "Card"]
```

For more details, see {doc}`services/component_registry`.

### ComponentLookup

**Purpose:** Bridge between string names and component instances with full dependency injection.

**Workflow:**
1. Look up component class type by name (ComponentNameRegistry)
2. Execute pre-resolution middleware (if registered)
3. Detect if component is async (check `__call__` method)
4. Get appropriate injector from container (sync or async)
5. Construct component instance with dependencies injected
6. Return the constructed component

**Usage:**
```python
lookup = ComponentLookup(container=container)

# Resolve sync component
button = lookup("Button", context={"label": "Submit"})
# Returns: Button instance with dependencies injected
output = button()  # Call to render

# Resolve async component
alert = lookup("Alert", context={"message": "Warning"})
# Returns: Coroutine (needs await)
output = await alert  # Then call to render
```

**Error handling:**
```python
try:
    component = lookup("Unknown", context={})
except ComponentNotFoundError:
    # Component name not registered
    pass
except InjectorNotFoundError:
    # Required injector not in container
    pass
except RegistryNotSetupError:
    # ComponentNameRegistry not registered
    pass
```

For more details, see {doc}`services/component_lookup`.

### scan_components()

**Purpose:** Automatically discover `@injectable` decorated classes and register them.

**How it works:**
1. Scan specified packages for modules
2. Find classes decorated with `@injectable`
3. Extract metadata (resource, location, etc.)
4. Register in both svcs.Registry and ComponentNameRegistry
5. Validate all items are classes (skip non-classes with warning)

**Usage:**
```python
from tdom_svcs import scan_components

# Scan packages for components
scan_components(
    registry,              # svcs.Registry
    component_registry,    # ComponentNameRegistry
    "app.components",      # Package to scan
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

# ComponentLookup detects async __call__ and returns coroutine
result = lookup("AsyncAlert", context={"message": "Warning"})
# result is a coroutine, needs await:
component = await result
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

Override a component everywhere in your application by registering it last:

```text
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
class CustomButton:
    label: str = "Click"
    theme: Inject[ThemeService]

    def __call__(self) -> str:
        color = self.theme.get_brand_color()
        return f"<button style='color: {color}'>{self.label}</button>"

# Register both - last one wins for global override
component_registry.register("Button", Button)
component_registry.register("Button", CustomButton)  # This one is used
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

Use `container.register_value()` to provide test doubles:

```text
import svcs
from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup

def test_button_with_fake_database():
    """Test component with a fake database service."""

    # Create fake service
    class FakeDatabaseService:
        def get_button_config(self):
            return {"color": "red", "size": "large"}

    # Setup container with fake
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    registry.register_value(DatabaseService, FakeDatabaseService())

    # Scan and setup components
    scan_components(registry, component_registry, __name__)
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    # Test with fake
    container = svcs.Container(registry)
    lookup = container.get(ComponentLookup)
    button = lookup("Button", context={"label": "Test"})
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
    registry = svcs.Registry()
    registry.register_value(DatabaseService, FakeDatabase())
    registry.register_value(CacheService, FakeCache())

    # Register and resolve component
    component_registry = ComponentNameRegistry()
    scan_components(registry, component_registry, __name__)
    # ... setup and test
```

### Integration Testing

Test end-to-end component resolution:

```text
def test_component_resolution_integration():
    """Integration test for complete component resolution flow."""

    # Setup real services (or fakes)
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register all services
    registry.register_value(DatabaseService, DatabaseService())
    registry.register_value(ThemeService, ThemeService())

    # Scan components
    scan_components(registry, component_registry, "myapp.components")

    # Setup infrastructure
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    # Test resolution
    container = svcs.Container(registry)
    lookup = container.get(ComponentLookup)

    button = lookup("Button", context={"label": "Submit"})
    output = button()

    assert "Submit" in output
    assert "<button" in output
```

For complete testing examples, see [examples/middleware/03_testing_with_fakes.py](../examples/middleware/03_testing_with_fakes.py).

## Complete Setup Example

Here's a complete application setup showing all the pieces together:

```python
import svcs
from svcs_di.injectors.locator import HopscotchInjector, HopscotchAsyncInjector
from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup

def setup_application() -> tuple[svcs.Registry, svcs.Container]:
    """Set up the application with dependency injection."""

    # Create registries
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services (non-component dependencies)
    from app.services.database import DatabaseService
    from app.services.auth import AuthService

    registry.register_value(DatabaseService, DatabaseService())
    registry.register_value(AuthService, AuthService())

    # Scan for @injectable components
    scan_components(
        registry,
        component_registry,
        "app.components",  # Your component package
    )

    # Register component infrastructure
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)
    registry.register_factory(HopscotchAsyncInjector, HopscotchAsyncInjector)

    # Register ComponentLookup service
    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    # Create container
    container = svcs.Container(registry)

    return registry, container

# Use in your application
registry, container = setup_application()

# Get ComponentLookup service
lookup = container.get(ComponentLookup)

# Resolve components by name
button = lookup("Button", context={"label": "Submit"})
output = button()  # Render component
```

## Best Practices

### 1. Use Class Components for Templates

Always use class components when you need string name resolution:

```python
# ✅ Good - can be referenced in templates as <Button>
@injectable
@dataclass
class Button:
    label: str = "Click"

    def __call__(self) -> str:
        return f"<button>{self.label}</button>"

# ❌ Bad - functions cannot be registered by name
def button(label: str = "Click") -> str:
    return f"<button>{label}</button>"
```

### 2. Use HopscotchInjector in Production

Always use HopscotchInjector for production applications:

```python
# ✅ Good - production-ready
from svcs_di.injectors.locator import HopscotchInjector
registry.register_factory(HopscotchInjector, HopscotchInjector)

# ❌ Bad - limited features, educational only
from svcs_di.injectors.keyword import KeywordInjector
registry.register_value(KeywordInjector, KeywordInjector(container))
```

### 3. Validate Early

Use `scan_components()` at application startup to catch errors early:

```python
# ✅ Good - errors happen at startup
def setup_application():
    scan_components(registry, component_registry, "app.components")
    # Any registration errors happen here, before serving requests
    return container

# ❌ Bad - errors happen during requests
def handle_request():
    # Component registration happens per-request
    component_registry.register("Button", Button)  # Too late!
```

### 4. Proper Field Order

Always put `Inject[]` fields before fields with defaults:

```python
# ✅ Good
@dataclass
class MyComponent:
    db: Inject[DatabaseService]  # No default - comes first
    name: str = "default"        # Has default - comes second

# ❌ Bad - causes TypeError
@dataclass
class MyComponent:
    name: str = "default"
    db: Inject[DatabaseService]  # Error: non-default after default
```

### 5. Use Type Hints

Always provide type hints for better IDE support and type checking:

```python
# ✅ Good - clear types
@dataclass
class Button:
    db: Inject[DatabaseService]
    label: str

    def __call__(self) -> str:
        return f"<button>{self.label}</button>"

# ❌ Bad - missing types
@dataclass
class Button:
    db: Inject[DatabaseService]
    label  # Type unclear

    def __call__(self):  # Return type unclear
        return f"<button>{self.label}</button>"
```

## Error Handling

### Common Errors and Solutions

#### ComponentNotFoundError

**Cause:** Component name not registered.

```python
try:
    component = lookup("UnknownComponent", context={})
except ComponentNotFoundError as e:
    print(f"Component not registered: {e}")
    # Solution: Check component name, ensure it's decorated with @injectable
```

#### InjectorNotFoundError

**Cause:** Required injector not in container.

```python
try:
    component = lookup("Button", context={})
except InjectorNotFoundError as e:
    print(f"Injector missing: {e}")
    # Solution: Register HopscotchInjector in setup:
    # registry.register_factory(HopscotchInjector, HopscotchInjector)
```

#### RegistryNotSetupError

**Cause:** ComponentNameRegistry not registered in container.

```python
try:
    component = lookup("Button", context={})
except RegistryNotSetupError as e:
    print(f"Registry not setup: {e}")
    # Solution: Register ComponentNameRegistry:
    # registry.register_value(ComponentNameRegistry, component_registry)
```

#### TypeError: non-default argument follows default argument

**Cause:** Dataclass field order violation - `Inject[]` field after field with default.

```python
# ❌ This fails:
@dataclass
class MyComponent:
    name: str = "default"
    db: Inject[DatabaseService]  # Error!

# ✅ Fix: Reorder fields
@dataclass
class MyComponent:
    db: Inject[DatabaseService]  # No default first
    name: str = "default"        # Default second
```

#### TypeError: only accepts class types

**Cause:** Attempting to register a function in ComponentNameRegistry.

```python
def my_function():
    return "hello"

try:
    component_registry.register("MyFunc", my_function)
except TypeError as e:
    print(f"Cannot register function: {e}")
    # Solution: Convert to a class component or call directly with injector
```

## Summary

tdom-svcs provides a powerful, type-safe way to integrate dependency injection with template-based rendering:

- **Class components** for template integration and string name resolution
- **Function components** for simple, direct usage (no template integration)
- **HopscotchInjector** for production with advanced resolution strategies
- **KeywordInjector** for educational function examples only
- **Type-safe** with `type[T]` generics and early validation
- **Flexible** with resource and location-based resolution
- **Easy setup** with `scan_components()` for automatic discovery
- **Middleware system** for lifecycle hooks and cross-cutting concerns
- **Override patterns** for customization (global, resource, location)
- **Testing patterns** with fakes for isolated unit tests

For more examples, see {doc}`examples` and the `examples/` directory in the repository.
