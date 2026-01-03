# ComponentNameRegistry Service

The **ComponentNameRegistry** service provides thread-safe mapping between string component names and Python class types. It's a core service that enables template-based component references.

## Overview

ComponentNameRegistry maintains a dictionary mapping string names to component class types (`dict[str, type]`). This allows templates to reference components by name (e.g., `<Button>`) while maintaining type safety throughout the resolution process.

### Purpose and Role

In tdom-svcs architecture, ComponentNameRegistry serves as the bridge between:
- **Templates:** Reference components by string names
- **Python classes:** Actual component implementations
- **ComponentLookup:** Resolves names to instances with DI

The registry validates that only class types can be registered, preventing common errors and ensuring type safety.

### Thread Safety

ComponentNameRegistry is designed for free-threaded Python 3.14+. It uses `threading.Lock` to ensure thread-safe access to the internal registry, making it safe for concurrent use in multi-threaded applications.

## Setup

### Creating an Instance

Create a ComponentNameRegistry instance during application setup:

```python
from tdom_svcs import ComponentNameRegistry

# Create the registry
component_registry = ComponentNameRegistry()
```

### Registering in Container

Register the ComponentNameRegistry instance in your svcs container so other services can access it:

```python
import svcs

registry = svcs.Registry()
component_registry = ComponentNameRegistry()

# Register as singleton
registry.register_value(ComponentNameRegistry, component_registry)

# Create container
container = svcs.Container(registry)

# Later, retrieve it
registry_service = container.get(ComponentNameRegistry)
```

## Registration API

### register()

Register a component class under a string name:

```python
from dataclasses import dataclass

@dataclass
class Button:
    label: str

# Register the component
component_registry.register("Button", Button)
```

If a component with the same name already exists, it will be overwritten:

```python
from dataclasses import dataclass

@dataclass
class ImprovedButton:
    label: str
    variant: str = "primary"

# This replaces the original Button registration
component_registry.register("ImprovedButton", ImprovedButton)
```

```{admonition} Class Types Only
:class: warning

ComponentNameRegistry only accepts class types. Attempting to register a function will raise a `TypeError` with a clear error message explaining that function components cannot be registered by string name.
```

**Example - error handling:**

```python
from tdom_svcs import ComponentNameRegistry

component_registry = ComponentNameRegistry()

# This will raise TypeError
def button_function(label: str) -> str:
    return f"<button>{label}</button>"

try:
    component_registry.register("Button", button_function)
except TypeError as e:
    # Error message explains the issue
    assert "only accepts class types" in str(e)
    assert "Function components" in str(e)
```

### get_type()

Retrieve a component class type by its registered name:

```python
from dataclasses import dataclass
from tdom_svcs import ComponentNameRegistry

component_registry = ComponentNameRegistry()

@dataclass
class Card:
    title: str

component_registry.register("Card", Card)

# Retrieve the type
card_type = component_registry.get_type("Card")
assert card_type is Card  # True

# Unknown names return None
unknown = component_registry.get_type("UnknownComponent")
assert unknown is None  # True
```

### get_all_names()

Get a list of all registered component names:

```python
from dataclasses import dataclass
from tdom_svcs import ComponentNameRegistry

component_registry = ComponentNameRegistry()

@dataclass
class Button:
    label: str

@dataclass
class Card:
    title: str

@dataclass
class Alert:
    message: str

component_registry.register("Button", Button)
component_registry.register("Card", Card)
component_registry.register("Alert", Alert)

# Get all registered names
all_names = component_registry.get_all_names()
assert sorted(all_names) == ['Alert', 'Button', 'Card']
```

This method is particularly useful for generating error messages when a component is not found.

## Usage with scan_components()

The most common way to populate ComponentNameRegistry is using `scan_components()`, which automatically discovers components decorated with `@injectable`:

Example code structure:

```text
# Define components in your package
@injectable
@dataclass
class Button:
    label: str = "Click"

@injectable
@dataclass
class Card:
    title: str = "Card"

# Set up registries
registry = svcs.Registry()
component_registry = ComponentNameRegistry()

# Automatically discover and register all @injectable components
scan_components(
    registry,              # svcs.Registry for DI
    component_registry,    # ComponentNameRegistry for name mapping
    __name__,              # Current module
)

# All @injectable classes are now registered
assert component_registry.get_type("Button") is Button
assert component_registry.get_type("Card") is Card
```

### Scanning Multiple Packages

Scan multiple packages to register components from different parts of your application:

```text
scan_components(
    registry,
    component_registry,
    "myapp.components",   # All components in this package
    "myapp.widgets",      # All widgets in this package
    "myapp.layouts",      # All layouts in this package
)
```

## Complete Example

Here's a complete example showing ComponentNameRegistry in a real application. See the full examples in the `examples/` directory for runnable code.

Example structure:

```text
from dataclasses import dataclass
import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import HopscotchInjector
from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup

# Define a service
class ThemeService:
    def get_color(self) -> str:
        return "#007bff"

# Define components
@injectable
@dataclass
class Button:
    theme: Inject[ThemeService]
    label: str = "Click"

    def __call__(self) -> str:
        color = self.theme.get_color()
        return f'<button style="color: {color}">{self.label}</button>'

# Set up application
def setup_application() -> tuple[svcs.Container, ComponentNameRegistry]:
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

    container = svcs.Container(registry)
    return container, component_registry

# Use the application
container, component_registry = setup_application()
lookup = container.get(ComponentLookup)
button = lookup("Button", context={"label": "Submit"})
print(button())  # <button style="color: #007bff">Submit</button>
```

## Best Practices

### 1. Register Early

Register components during application startup, not per-request:

```text
# ✅ Good - register once at startup
def setup_application():
    scan_components(registry, component_registry, "myapp.components")
    return container

# ❌ Bad - don't register per-request
def handle_request():
    component_registry.register("Button", Button)  # Too late!
```

### 2. Use scan_components()

Prefer automatic discovery over manual registration:

```text
# ✅ Good - automatic discovery
scan_components(registry, component_registry, "myapp.components")

# ❌ Bad - manual registration (error-prone)
component_registry.register("Button", Button)
component_registry.register("Card", Card)
# ... easy to forget components
```

### 3. Validate Registration

Check that expected components are registered:

```python
from tdom_svcs import ComponentNameRegistry

component_registry = ComponentNameRegistry()

# Validate critical components are available
critical_components = ["Button", "Card", "Layout"]
registered = component_registry.get_all_names()

missing = [comp for comp in critical_components if comp not in registered]
if missing:
    print(f"Missing components: {missing}")
```

## Error Handling

### TypeError: only accepts class types

**Cause:** Attempting to register a function or non-class type.

**Solution:** Convert to a class component:

```text
# ❌ Function - cannot register
def my_widget(label: str) -> str:
    return f"<div>{label}</div>"

# ✅ Class - can register
@dataclass
class MyWidget:
    label: str

    def __call__(self) -> str:
        return f"<div>{self.label}</div>"
```

### Component Not Found

When a component name is not found, use `get_all_names()` to help users:

```python
from tdom_svcs import ComponentNameRegistry

component_registry = ComponentNameRegistry()

# Example of building helpful error message
name = "UnknownComponent"
component_type = component_registry.get_type(name)

if component_type is None:
    all_names = component_registry.get_all_names()
    message = f"Component '{name}' not found."
    if all_names:
        message += f" Available components: {', '.join(sorted(all_names))}"
    print(message)
```

## See Also

- {doc}`../core_concepts` - Understand components and registries
- {doc}`component_lookup` - Resolve components by name
- {doc}`../how_it_works` - Deep dive into architecture
- {doc}`../examples` - More usage examples
