# Core Concepts

This guide covers the fundamental concepts of tdom-svcs: components, dependency injection, service containers, and component registries.

## Components

Components are reusable building blocks that render HTML or other output. tdom-svcs supports two types of components with different capabilities.

### Class Components

**Class components** are the recommended approach for production use. They are Python classes (typically dataclasses) that can be:

- Registered by string name in ComponentNameRegistry
- Discovered automatically via `@injectable` decorator
- Resolved by name using ComponentLookup
- Referenced in templates

**Example:**

```python
from dataclasses import dataclass
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable

@injectable
@dataclass
class Button:
    """A button component with dependency injection."""

    theme: Inject[ThemeService]  # Injected from container
    label: str = "Click"          # Regular parameter with default
    disabled: bool = False        # Regular parameter with default

    def __call__(self) -> str:
        """Render the button."""
        color = self.theme.get_button_color()
        disabled_attr = " disabled" if self.disabled else ""
        return f'<button style="color: {color}"{disabled_attr}>{self.label}</button>'
```

**Key characteristics:**
- Must be classes (not functions)
- Use `@injectable` for automatic discovery
- Use `Inject[]` for dependencies
- Implement `__call__()` to render output

### Function Components

**Function components** are simpler but have limited capabilities. They can use `Inject[]` but cannot be registered by name or referenced in templates.

**Example:**

```python
from svcs_di import Inject

def simple_widget(
    label: str,
    theme: Inject[ThemeService]  # Can use Inject[]
) -> str:
    """A simple widget function."""
    color = theme.get_color()
    return f"<div style='color: {color}'>{label}</div>"
```

**Limitations:**
- Cannot be registered in ComponentNameRegistry
- Cannot be discovered via `@injectable`
- Cannot be resolved by ComponentLookup
- Must be called directly with an injector

```{admonition} Use Class Components for Templates
:class: tip

Always use class components when you need to reference components by name in templates. Function components are only suitable for direct programmatic use.
```

## Dependency Injection

Dependency injection (DI) is the core pattern that makes components testable and maintainable. Instead of creating dependencies inside components, you declare what you need and let the container provide it.

### Using Inject[]

Mark dependencies with `Inject[]` to have them automatically provided:

```python
from dataclasses import dataclass
from svcs_di import Inject

@dataclass
class UserProfile:
    """Component showing user profile."""

    db: Inject[DatabaseService]    # Injected
    cache: Inject[CacheService]    # Injected
    user_id: int                    # From context

    def __call__(self) -> str:
        # Use injected dependencies
        user = self.db.get_user(self.user_id)
        cached = self.cache.get(f"user_{self.user_id}")
        return f"<div>{user['name']}</div>"
```

### Field Ordering in Dataclasses

Python dataclasses require fields without defaults to come before fields with defaults:

```python
# ✅ Correct - Inject[] fields (no default) first
@dataclass
class MyComponent:
    db: Inject[DatabaseService]      # No default
    cache: Inject[CacheService]      # No default
    title: str = "Default"           # Has default
    enabled: bool = True             # Has default

# ❌ Wrong - causes TypeError
@dataclass
class MyComponent:
    title: str = "Default"           # Has default first
    db: Inject[DatabaseService]      # No default second - ERROR!
```

### Mixing Dependencies and Parameters

Components often need both injected dependencies and regular parameters:

```python
@dataclass
class ProductCard:
    """Product card with price service dependency."""

    pricing: Inject[PricingService]  # Injected from container
    product_id: int                   # Required from context
    quantity: int = 1                 # Optional from context

    def __call__(self) -> str:
        price = self.pricing.get_price(self.product_id, self.quantity)
        return f"<div>Price: ${price}</div>"
```

When resolving:
- `pricing` is automatically injected from the container
- `product_id` and `quantity` come from the context parameter

## Service Container

The **service container** is the registry of all services and components in your application. It's powered by the `svcs` library.

### Registry vs Container

- **Registry (`svcs.Registry`):** Defines what services are available and how to create them
- **Container (`svcs.Container`):** Provides access to service instances at runtime

```python
import svcs

# Create registry and define services
registry = svcs.Registry()
registry.register_value(DatabaseService, DatabaseService())
registry.register_factory(CacheService, create_cache)

# Create container to access services
container = svcs.Container(registry)

# Get services from container
db = container.get(DatabaseService)
cache = container.get(CacheService)
```

### Registration Patterns

**Register by value** (singleton):

```python
service = DatabaseService()
registry.register_value(DatabaseService, service)
```

**Register by factory** (created on demand):

```python
def create_cache() -> CacheService:
    return CacheService(max_size=1000)

registry.register_factory(CacheService, create_cache)
```

**Register with factory class** (for injectors):

```python
from svcs_di.injectors.locator import HopscotchInjector

registry.register_factory(HopscotchInjector, HopscotchInjector)
```

## ComponentNameRegistry

The **ComponentNameRegistry** service maps string component names to class types. This enables template-based component references.

### Basic Usage

```python
from tdom_svcs import ComponentNameRegistry

# Create registry
registry = ComponentNameRegistry()

# Register components by name
registry.register("Button", Button)
registry.register("Card", Card)

# Retrieve component types
button_class = registry.get_type("Button")  # Returns: type[Button]
unknown = registry.get_type("Unknown")       # Returns: None

# List all registered names
all_names = registry.get_all_names()  # Returns: ["Button", "Card"]
```

### Automatic Registration

Use `scan_components()` to automatically discover and register components:

```python
from tdom_svcs import scan_components

# Scan packages for @injectable components
scan_components(
    registry,              # svcs.Registry
    component_registry,    # ComponentNameRegistry
    "myapp.components",    # Package to scan
    "myapp.widgets",       # Another package
)
```

This finds all classes decorated with `@injectable` and registers them in both registries.

```{admonition} Class Components Only
:class: warning

ComponentNameRegistry only accepts class types. Attempting to register a function will raise a TypeError with a helpful error message.
```

## ComponentLookup

The **ComponentLookup** service resolves component names to instances with full dependency injection. It bridges string names (from templates) to Python objects.

### Resolution Workflow

When you call `lookup("Button", context={...})`, ComponentLookup:

1. Looks up the component class type by name (ComponentNameRegistry)
2. Executes pre-resolution middleware (if registered)
3. Detects if the component is async
4. Gets the appropriate injector (sync or async)
5. Constructs the component with dependencies injected
6. Returns the constructed component

### Basic Usage

```python
from tdom_svcs.services.component_lookup import ComponentLookup

# Get ComponentLookup from container
lookup = container.get(ComponentLookup)

# Resolve sync component
button = lookup("Button", context={"label": "Submit", "disabled": False})
output = button()  # Render component

# Resolve async component
alert = lookup("AsyncAlert", context={"message": "Warning"})
component = await alert  # Await construction
output = await component()  # Render
```

### Error Handling

ComponentLookup provides clear error messages:

```python
from tdom_svcs.services.component_lookup.exceptions import (
    ComponentNotFoundError,
    InjectorNotFoundError,
    RegistryNotSetupError,
)

try:
    component = lookup("Unknown", context={})
except ComponentNotFoundError as e:
    print(f"Component not registered: {e}")
except InjectorNotFoundError as e:
    print(f"Injector missing: {e}")
except RegistryNotSetupError as e:
    print(f"Registry not setup: {e}")
```

## Putting It All Together

Here's a complete example showing all concepts:

```python
from dataclasses import dataclass

import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import HopscotchInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup


# 1. Define services
class ThemeService:
    """Service providing theme colors."""

    def get_button_color(self) -> str:
        return "#007bff"


# 2. Define components
@injectable
@dataclass
class Button:
    """Button component with theme service."""

    theme: Inject[ThemeService]  # Dependency injection
    label: str = "Click"          # Regular parameter

    def __call__(self) -> str:
        color = self.theme.get_button_color()
        return f'<button style="color: {color}">{self.label}</button>'


# 3. Set up container
def setup_application() -> svcs.Container:
    """Set up the application with all services."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Register services
    registry.register_value(ThemeService, ThemeService())

    # Discover components
    scan_components(registry, component_registry, __name__)

    # Register infrastructure
    registry.register_value(ComponentNameRegistry, component_registry)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    return svcs.Container(registry)


# 4. Use the application
if __name__ == "__main__":
    container = setup_application()
    lookup = container.get(ComponentLookup)

    # Resolve and render component
    button = lookup("Button", context={"label": "Submit"})
    print(button())  # <button style="color: #007bff">Submit</button>
```

## Next Steps

- {doc}`how_it_works` - Deep dive into architecture and advanced features
- {doc}`services/component_registry` - Detailed ComponentNameRegistry documentation
- {doc}`services/component_lookup` - Detailed ComponentLookup documentation
- {doc}`examples` - Browse more examples
