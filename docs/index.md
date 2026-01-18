# tdom-svcs Documentation

TDOM integration with svcs dependency injection.

## Overview

**tdom-svcs** provides a powerful integration layer between TDOM (Template DOM) and the svcs dependency injection library. It enables component-based template rendering with automatic dependency resolution, making it easy to build maintainable, testable applications using Python 3.14+ and PEP 750 template strings.

### Key Features

- **Type-safe component resolution:** Resolve components directly by type from the container
- **Automatic dependency injection:** Use `Inject[]` to declare dependencies
- **Component discovery:** Automatically find and register components via `@injectable`
- **Middleware system:** Add lifecycle hooks for logging, validation, and transformation
- **Multi-tenancy support:** Resource and location-based component resolution
- **Thread-safe:** Built for free-threaded Python 3.14+
- **Type-safe:** Full type hinting with generics for IDE support

### Architecture

tdom-svcs provides core services:

1. **HopscotchRegistry/HopscotchContainer:** Extended registry and container with built-in DI support
2. **MiddlewareManager:** Executes lifecycle hooks during component resolution

## Quick Links

- {doc}`getting_started` - Install and create your first component
- {doc}`core_concepts` - Understand components, DI, and registries
- {doc}`how_it_works` - Deep dive into architecture and patterns
- {doc}`examples` - Browse working examples
- {doc}`api_reference` - API documentation

### Services Documentation

- {doc}`services/middleware` - MiddlewareManager service

## Contents

```{toctree}
:maxdepth: 2

getting_started
core_concepts
how_it_works
services/middleware
examples
api_reference
```

## Installation

To install tdom-svcs, use uv or pip:

```bash
uv add tdom-svcs
```

Or:

```bash
pip install tdom-svcs
```

## Simple Example

Here's a minimal example showing dependency injection with a class component:

```python
from dataclasses import dataclass
from svcs_di import HopscotchContainer, HopscotchRegistry, Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import scan

# Define a service
class DatabaseService:
    def get_data(self) -> str:
        return "data from database"

# Define a component with dependency injection
@injectable
@dataclass
class DataDisplay:
    db: Inject[DatabaseService]  # Automatically injected
    title: str = "Display"        # Regular parameter

    def __call__(self) -> str:
        data = self.db.get_data()
        return f"<div><h2>{self.title}</h2><p>{data}</p></div>"

# Setup and use
registry = HopscotchRegistry()
registry.register_value(DatabaseService, DatabaseService())
scan(registry, __name__)

with HopscotchContainer(registry) as container:
    component = container.inject(DataDisplay)
    output = component()
```

Components are automatically discovered via `@injectable`, dependencies are injected automatically, and you resolve them using `container.inject()`.

## Next Steps

1. Follow the {doc}`getting_started` guide to set up your first application
2. Read {doc}`core_concepts` to understand the fundamental concepts
3. Explore {doc}`examples` for real-world patterns
4. Dive into {doc}`how_it_works` for advanced topics
