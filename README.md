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

- **Python 3.14+** (uses PEP 695 generics and modern type parameter syntax)
- **tdom**
- **svcs**

## Overview

tdom-svcs bridges template-based component rendering (tdom) with dependency injection (svcs). It provides:

- **Type-safe component resolution** - Resolve components directly by type using `container.get(ComponentType)`
- **Automatic dependency injection** - Use `Inject[]` for automatic service resolution in component parameters
- **Component discovery** - Scan packages for `@injectable` components
- **Type-safe** - Full type hints with `type[T]` generics
- **Production-ready** - Resource and location-based resolution with HopscotchInjector

## Quick Start

```python
import svcs
from dataclasses import dataclass
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import HopscotchInjector, scan


# Define a component with dependency injection
@injectable
@dataclass
class Button:
    db: Inject[DatabaseService]  # Automatically injected
    label: str = "Click"  # Regular parameter

    def __call__(self) -> str:
        config = self.db.get_button_config()
        return f"<button>{self.label}</button>"


# Setup application
registry = svcs.Registry()

# Register services
registry.register(DatabaseService, DatabaseService)

# Scan for components
scan(registry, "app.components")

# Register injector
registry.register_factory(HopscotchInjector, HopscotchInjector)

# Create container and resolve components
container = svcs.Container(registry)

# Resolve component by type
button = container.get(Button)
output = button()  # <button>Click</button>
```

## Key Concepts

### Class vs Function Components

- **Class components** use the `@injectable` decorator and can be registered for DI
- **Function components** can use `Inject[]` but are best called directly with an injector

### Injector Selection

- **HopscotchInjector** (production) - Supports resource/location-based resolution
- **KeywordInjector** (educational) - Simple cases, function components only

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
