# Getting Started

This guide will help you install tdom-svcs and create your first dependency-injected component.

## Prerequisites

```{admonition} Python 3.14+ Required
:class: warning

tdom-svcs requires Python 3.14 or later because it leverages PEP 750 template strings (t-strings) for TDOM integration. Make sure you have Python 3.14+ installed before proceeding.
```

**Required:**
- Python 3.14 or later
- Understanding of Python dataclasses
- Basic knowledge of type hints

**Helpful:**
- Familiarity with dependency injection concepts
- Experience with web frameworks or template systems

## Installation

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer:

```bash
uv add tdom-svcs
```

### Using pip

Alternatively, install with pip:

```bash
pip install tdom-svcs
```

This will install tdom-svcs and its dependencies:
- `svcs` - Service container
- `svcs-di` - Dependency injection framework
- `tdom` - Template DOM library

## Quickstart

Let's build a simple component with dependency injection in 4 steps.

### Step 1: Define a Service

Services are regular Python classes that provide functionality:

```python
class GreetingService:
    """Service that provides greeting messages."""

    def get_greeting(self, name: str) -> str:
        return f"Hello, {name}!"
```

### Step 2: Define a Component

Components use the `@injectable` decorator and `Inject[]` for dependencies:

```python
from dataclasses import dataclass
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable

@injectable
@dataclass
class Greeting:
    """Component that displays a greeting."""

    service: Inject[GreetingService]  # Injected dependency
    name: str = "World"                # Regular parameter with default

    def __call__(self) -> str:
        """Render the component."""
        message = self.service.get_greeting(self.name)
        return f"<div>{message}</div>"
```

```{admonition} Field Order Matters
:class: tip

In dataclasses, fields without defaults (`Inject[]` fields) must come before fields with defaults. This is a Python requirement, not a tdom-svcs restriction.
```

### Step 3: Set Up the Container

Register your services and components with `HopscotchRegistry` and `HopscotchContainer`:

```python
from svcs_di import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.locator import scan

# Create registry
registry = HopscotchRegistry()

# Register the greeting service
greeting_service = GreetingService()
registry.register_value(GreetingService, greeting_service)

# Scan for @injectable components (discovers Greeting)
scan(registry, __name__)

# Create container
container = HopscotchContainer(registry)
```

### Step 4: Use Your Component

Resolve components using `inject()` and render them:

```python
# Resolve component with dependency injection
greeting = container.inject(Greeting)

# Render the component
output = greeting()
print(output)  # <div>Hello, World!</div>

# Or with custom parameters
greeting_custom = container.inject(Greeting, name="Alice")
output = greeting_custom()
print(output)  # <div>Hello, Alice!</div>
```

## Complete Example

Here's the full working example:

```python
from dataclasses import dataclass

from svcs_di import HopscotchContainer, HopscotchRegistry, Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import scan


# Step 1: Define service
class GreetingService:
    """Service that provides greeting messages."""

    def get_greeting(self, name: str) -> str:
        return f"Hello, {name}!"


# Step 2: Define component
@injectable
@dataclass
class Greeting:
    """Component that displays a greeting."""

    service: Inject[GreetingService]  # Injected dependency
    name: str = "World"                # Regular parameter with default

    def __call__(self) -> str:
        """Render the component."""
        message = self.service.get_greeting(self.name)
        return f"<div>{message}</div>"


# Step 3: Set up container
def setup() -> HopscotchContainer:
    """Set up the application container."""
    registry = HopscotchRegistry()

    # Register services
    greeting_service = GreetingService()
    registry.register_value(GreetingService, greeting_service)

    # Scan for components
    scan(registry, __name__)

    return HopscotchContainer(registry)


# Step 4: Use the component
if __name__ == "__main__":
    container = setup()

    # Resolve component with dependency injection
    greeting = container.inject(Greeting)
    output = greeting()
    print(output)  # <div>Hello, World!</div>
```

## Next Steps

Now that you have a working component, explore:

- {doc}`core_concepts` - Learn about components, DI, and registries
- {doc}`how_it_works` - Understand the architecture in depth
- {doc}`examples/index` - See more complex patterns and use cases
- {doc}`services/middleware` - Add lifecycle hooks to your components

## Common Issues

### TypeError: non-default argument follows default argument

This happens when dataclass fields are in the wrong order. Fix by putting `Inject[]` fields first:

```python
# ❌ Wrong - causes TypeError
@dataclass
class MyComponent:
    name: str = "default"        # Has default
    db: Inject[DatabaseService]  # No default - ERROR!

# ✅ Correct
@dataclass
class MyComponent:
    db: Inject[DatabaseService]  # No default first
    name: str = "default"        # Default second
```

### ComponentNotFoundError

Component name not registered. Check:
- Is the component decorated with `@injectable`?
- Did you call `scan()` with the correct package name?
- Is the component a class (not function)?

### Service Not Found

If `container.inject()` or `container.get()` fails to find a service:
- Check that you registered the service with `registry.register_value()` or `registry.register_factory()`
- Verify the service type matches exactly (no subclasses unless you use protocols)
