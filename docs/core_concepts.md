# Core Concepts

This guide covers the fundamental concepts of tdom-svcs: components, dependency injection, service containers, and component registries.

## Components

Components are reusable building blocks that render HTML or other output. tdom-svcs supports two types of components with different capabilities.

### Class Components

**Class components** are the recommended approach for production use. They are Python classes (typically dataclasses) that can be:

- Discovered automatically via `@injectable` decorator
- Resolved directly from the container by type
- Use dependency injection via `Inject[]`

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
- Resolve with `container.get(Button)`

### Function Components

**Function components** are simpler but have limited capabilities. They can use `Inject[]` but should be called directly with an injector.

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
- Cannot be discovered via `@injectable`
- Must be called directly with an injector (not via container)

```{admonition} Use Class Components for Production
:class: tip

Always use class components for production applications. Function components are suitable for simple, direct programmatic use only.
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

The **service container** is the registry of all services and components in your application. tdom-svcs uses `HopscotchRegistry` and `HopscotchContainer` from svcs-di.

### Registry vs Container

- **HopscotchRegistry:** Extends `svcs.Registry` with built-in `ServiceLocator` for multi-implementation support
- **HopscotchContainer:** Extends `svcs.Container` with built-in `inject()` method for dependency injection

```python
from svcs_di import HopscotchContainer, HopscotchRegistry

# Create registry and define services
registry = HopscotchRegistry()
registry.register_value(DatabaseService, DatabaseService())
registry.register_factory(CacheService, create_cache)

# Create container with built-in inject()
with HopscotchContainer(registry) as container:
    # Get services directly
    db = container.get(DatabaseService)

    # Or inject with automatic dependency resolution
    component = container.inject(MyComponent)
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

**Register with multi-implementation** (for resource/location-based resolution):

```python
from pathlib import PurePath

# Default implementation
registry.register_implementation(Dashboard, DefaultDashboard)

# Admin-specific implementation
registry.register_implementation(Dashboard, AdminDashboard, location=PurePath("/admin"))
```

## Putting It All Together

Here's a complete example showing all concepts:

```python
from dataclasses import dataclass

from svcs_di import HopscotchContainer, HopscotchRegistry, Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import scan


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
def setup_application() -> HopscotchContainer:
    """Set up the application with all services."""
    registry = HopscotchRegistry()

    # Register services
    registry.register_value(ThemeService, ThemeService())

    # Discover components
    scan(registry, __name__)

    return HopscotchContainer(registry)


# 4. Use the application
if __name__ == "__main__":
    with setup_application() as container:
        # Resolve component with inject() and render
        button = container.inject(Button)
        print(button())  # <button style="color: #007bff">Click</button>
```

## Next Steps

- {doc}`how_it_works` - Deep dive into architecture and advanced features
- {doc}`services/middleware` - Add lifecycle hooks to components
- {doc}`examples` - Browse more examples
