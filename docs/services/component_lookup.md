# ComponentLookup Service

The **ComponentLookup** service resolves component names to instances with full dependency injection. It bridges string-based component references (from templates) to Python objects with automatic dependency resolution.

## Overview

ComponentLookup is the core service that connects all parts of tdom-svcs together:
- Uses **ComponentNameRegistry** to map names to types
- Integrates **MiddlewareManager** for lifecycle hooks
- Selects appropriate **injector** (sync or async)
- Constructs components with dependencies automatically injected

### Purpose and Role

ComponentLookup acts as the bridge between:
- **Template strings:** `<Button label="Submit">`
- **Component classes:** `class Button with Inject[] dependencies`
- **Service container:** Provides injected dependencies
- **Component instances:** Ready to render output

This abstraction allows templates to remain declarative while components benefit from full dependency injection.

## Setup

### Creating an Instance

ComponentLookup requires a configured svcs.Container:

```text
import svcs
from tdom_svcs.services.component_lookup import ComponentLookup

# Assume container is set up with all necessary services
lookup = ComponentLookup(container=container)
```

### Required Dependencies

ComponentLookup depends on several services being registered in the container:

1. **ComponentNameRegistry:** Maps names to types
2. **HopscotchInjector:** Constructs sync components
3. **HopscotchAsyncInjector:** Constructs async components (if using async)
4. **MiddlewareManager:** Optional, for middleware support

### Registration as Service

Register ComponentLookup as a service so other parts of your application can access it:

```text
def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
    return ComponentLookup(container=container)

registry.register_factory(ComponentLookup, component_lookup_factory)

# Later, retrieve it
lookup = container.get(ComponentLookup)
```

## Resolution Workflow

When you call `lookup("Button", context={...})`, ComponentLookup executes the following steps:

### Step 1: Registry Lookup

Look up the component class type by name using ComponentNameRegistry:

```text
component_type = registry.get_type("Button")  # Returns: type[Button]
```

If the name is not found, raises `ComponentNotFoundError`.

### Step 2: Pre-Resolution Middleware

Execute middleware in the pre-resolution phase:
- Global middleware from MiddlewareManager (if registered)
- Per-component middleware (if defined on component)
- Middleware can modify props or halt execution

### Step 3: Async Detection

Check if the component's `__call__` method is async:

```text
is_async = inspect.iscoroutinefunction(component_type.__call__)
```

### Step 4: Injector Selection

Select the appropriate injector based on async detection:
- **Sync components:** Use `HopscotchInjector`
- **Async components:** Use `HopscotchAsyncInjector`

### Step 5: Component Construction

Use the injector to construct the component with dependencies:

```text
# Sync construction
injector = container.get(HopscotchInjector)
component = injector(component_type)  # Dependencies automatically injected

# Async construction
injector = container.get(HopscotchAsyncInjector)
component = await injector(component_type)  # Async construction
```

### Step 6: Return Component

Return the constructed component, ready to be called for rendering.

## Basic Usage

### Resolving Sync Components

```text
from tdom_svcs.services.component_lookup import ComponentLookup

# Get ComponentLookup from container
lookup = container.get(ComponentLookup)

# Resolve component by name
button = lookup("Button", context={"label": "Submit", "disabled": False})

# Component is constructed with dependencies injected
# Now call it to render
output = button()  # Returns: "<button>Submit</button>"
```

### Resolving Async Components

```text
# Resolve async component
async_alert = lookup("AsyncAlert", context={"message": "Warning"})

# ComponentLookup returns a coroutine for async components
component = await async_alert

# Now call the component (which may also be async)
output = await component()  # Returns: "<div>Warning</div>"
```

### Using Context Parameter

The context parameter provides values for non-injected component fields:

```text
# Component definition:
@dataclass
class ProductCard:
    db: Inject[DatabaseService]  # Injected
    product_id: int               # From context
    quantity: int = 1             # From context or default

# Resolution with context:
card = lookup("ProductCard", context={"product_id": 123, "quantity": 2})

# - db: automatically injected from container
# - product_id: provided by context (123)
# - quantity: provided by context (2)
```

## Error Handling

ComponentLookup provides three specific exceptions with clear error messages.

### ComponentNotFoundError

**Cause:** Component name not registered in ComponentNameRegistry.

```python
from tdom_svcs.services.component_lookup.exceptions import ComponentNotFoundError

# Example of catching the error
try:
    # This would fail if lookup and context were defined
    pass  # component = lookup("UnknownComponent", context={})
except ComponentNotFoundError as e:
    print(f"Component not found: {e}")
```

### Injector Not Found Error

**Cause:** Required injector not registered in container.

```text
from tdom_svcs.services.component_lookup.exceptions import InjectorNotFoundError

try:
    component = lookup("Button", context={})
except InjectorNotFoundError as e:
    print(f"Injector missing: {e}")
    # Solution: Register the injector
    # registry.register_factory(HopscotchInjector, HopscotchInjector)
```

### Registry Not Setup Error

**Cause:** ComponentNameRegistry not registered in container.

```text
from tdom_svcs.services.component_lookup.exceptions import RegistryNotSetupError

try:
    component = lookup("Button", context={})
except RegistryNotSetupError as e:
    print(f"Registry not setup: {e}")
    # Solution: Register ComponentNameRegistry
    # registry.register_value(ComponentNameRegistry, component_registry)
```

## Integration with HopscotchInjector

ComponentLookup uses HopscotchInjector for production component resolution. This injector provides advanced features:

### Resource-Based Resolution

Components can be registered for specific resource contexts:

```text
@injectable(resource=CustomerContext)
@dataclass
class CustomerDashboard:
    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        return "<div>Customer Dashboard</div>"

@injectable(resource=AdminContext)
@dataclass
class AdminDashboard:
    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        return "<div>Admin Dashboard</div>"

# HopscotchInjector selects correct implementation based on resource
lookup("Dashboard", context={"resource": CustomerContext})
```

### Location-Based Resolution

Components can be registered for specific URL paths:

```text
@injectable(location=PurePath("/"))
@dataclass
class HomePage:
    content: Inject[ContentService]

    def __call__(self) -> str:
        return "<div>Home</div>"

@injectable(location=PurePath("/admin"))
@dataclass
class AdminPage:
    auth: Inject[AuthService]

    def __call__(self) -> str:
        return "<div>Admin Panel</div>"

# HopscotchInjector selects based on location
lookup("Page", context={"location": PurePath("/admin")})
```

## Complete Example

Here's a complete example showing ComponentLookup with all features. This example is illustrative - see `examples/` directory for runnable code.

```text
from dataclasses import dataclass
import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import HopscotchInjector, HopscotchAsyncInjector
from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup

# Define services
class DatabaseService:
    def get_data(self, id: int) -> dict:
        return {"id": id, "name": "Example"}

# Define sync component
@injectable
@dataclass
class DataCard:
    db: Inject[DatabaseService]
    item_id: int

    def __call__(self) -> str:
        data = self.db.get_data(self.item_id)
        return f"<div>{data['name']}</div>"

# Define async component
@injectable
@dataclass
class AsyncAlert:
    message: str = "Alert"

    async def __call__(self) -> str:
        # Simulate async operation
        return f"<div class='alert'>{self.message}</div>"

# Set up application
def setup_application() -> svcs.Container:
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services
    registry.register_value(DatabaseService, DatabaseService())

    # Discover components
    scan_components(registry, component_registry, __name__)

    # Register infrastructure
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)
    registry.register_factory(HopscotchAsyncInjector, HopscotchAsyncInjector)

    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    return svcs.Container(registry)

# Use the application
container = setup_application()
lookup = container.get(ComponentLookup)

# Resolve sync component
card = lookup("DataCard", context={"item_id": 42})
print(card())  # <div>Example</div>

# Resolve async component
async def main():
    alert = lookup("AsyncAlert", context={"message": "Success"})
    component = await alert
    output = await component()
    print(output)  # <div class='alert'>Success</div>
```

## Best Practices

### 1. Handle Errors Gracefully

Always handle ComponentLookup exceptions:

```text
from tdom_svcs.services.component_lookup.exceptions import (
    ComponentNotFoundError,
    InjectorNotFoundError,
    RegistryNotSetupError,
)

try:
    component = lookup(component_name, context=context)
except ComponentNotFoundError:
    # Component not registered - maybe show error page
    return render_error("Component not found")
except InjectorNotFoundError:
    # Setup error - log and fail fast
    logger.error("Injector not configured")
    raise
except RegistryNotSetupError:
    # Setup error - log and fail fast
    logger.error("Registry not configured")
    raise
```

### 2. Validate Setup

Check that all required services are registered:

```text
# During application startup
def validate_setup(container: svcs.Container) -> None:
    """Validate that all required services are registered."""
    try:
        container.get(ComponentNameRegistry)
        container.get(HopscotchInjector)
        container.get(ComponentLookup)
    except svcs.exceptions.ServiceNotFoundError as e:
        raise RuntimeError(f"Required service not registered: {e}")
```

### 3. Use Type Hints

ComponentLookup returns `Any` to support both sync and async components. Use type hints to clarify usage:

```text
# Sync component
button: Button = lookup("Button", context={...})

# Async component (returns coroutine)
alert_coro = lookup("AsyncAlert", context={...})
alert: AsyncAlert = await alert_coro
```

## See Also

- {doc}`../core_concepts` - Understand component resolution
- {doc}`component_registry` - ComponentNameRegistry service
- {doc}`middleware` - Middleware integration
- {doc}`../how_it_works` - Architecture deep dive
- {doc}`../examples` - More examples
