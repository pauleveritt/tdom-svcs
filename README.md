# tdom-svcs

TDOM integration with svcs dependency injection.

## Installation

```bash
$ uv add tdom-svcs
```

Or using pip:

```bash
$ pip install tdom-svcs
```

## Requirements

- **svcs**
- **Python 3.14+** (uses PEP 695 generics and modern type parameter syntax)

## Overview

tdom-svcs bridges template-based component rendering (tdom) with dependency injection (svcs). It provides:

- **String name resolution** - Reference components by name in templates (`<Button>`)
- **Automatic dependency injection** - Use `Inject[]` for automatic service resolution
- **Component discovery** - Scan packages for `@injectable` components
- **Type-safe** - Full type hints with `type[T]` generics
- **Production-ready** - Resource and location-based resolution with HopscotchInjector

## Quick Start

```python
import svcs
from dataclasses import dataclass
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import HopscotchInjector
from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup

# Define a component with dependency injection
@injectable
@dataclass
class Button:
    db: Inject[DatabaseService]  # Automatically injected
    label: str = "Click"         # Regular parameter

    def __call__(self) -> str:
        config = self.db.get_button_config()
        return f"<button>{self.label}</button>"

# Setup application
registry = svcs.Registry()
component_registry = ComponentNameRegistry()

# Register services
registry.register_value(DatabaseService, DatabaseService())

# Scan for components
scan_components(registry, component_registry, "app.components")

# Register infrastructure
registry.register_value(ComponentNameRegistry, component_registry)
registry.register_factory(HopscotchInjector, HopscotchInjector)
registry.register_factory(
    ComponentLookup,
    lambda container: ComponentLookup(container=container)
)

# Create container and resolve components
container = svcs.Container(registry)
lookup = container.get(ComponentLookup)

# Resolve component by name
button = lookup("Button", context={"label": "Submit"})
output = button()  # <button>Submit</button>
```

## Key Concepts

### Class vs Function Components

- **Class components** can be registered by name and used in templates
- **Function components** can use `Inject[]` but cannot be registered by name
- Only classes work with ComponentLookup and template string resolution

### Injector Selection

- **HopscotchInjector** (production) - Supports resource/location-based resolution
- **KeywordInjector** (educational) - Simple cases, function components only

For production code with ComponentLookup, always use HopscotchInjector.

## Documentation

See [How It Works](docs/how_it_works.md) for comprehensive documentation covering:
- Component type policy and best practices
- Injector usage and selection
- Type hinting approach
- Dependency injection with `Inject[]`
- Resource and location-based resolution
- Error handling and troubleshooting

## Testing

```bash
# Run tests
pytest

# Run tests in parallel
pytest -n auto

# Run with coverage
pytest --cov=tdom_svcs
```
