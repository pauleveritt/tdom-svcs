# tdom-svcs Documentation

TDOM integration with svcs dependency injection.

## Overview

**tdom-svcs** provides a powerful integration layer between TDOM (Template DOM) and the svcs dependency injection library. It enables component-based template rendering with automatic dependency resolution, making it easy to build maintainable, testable applications using Python 3.14+ and PEP 750 template strings.

### Key Features

- **String-based component resolution:** Reference components by name in templates
- **Automatic dependency injection:** Use `Inject[]` to declare dependencies
- **Component discovery:** Automatically find and register components via `@injectable`
- **Middleware system:** Add lifecycle hooks for logging, validation, and transformation
- **Multi-tenancy support:** Resource and location-based component resolution
- **Thread-safe:** Built for free-threaded Python 3.14+
- **Type-safe:** Full type hinting with generics for IDE support

### Architecture

tdom-svcs provides three core services:

1. **ComponentNameRegistry:** Maps string names to component class types
2. **ComponentLookup:** Resolves component names to instances with full DI
3. **MiddlewareManager:** Executes lifecycle hooks during component resolution

## Quick Links

- {doc}`getting_started` - Install and create your first component
- {doc}`core_concepts` - Understand components, DI, and registries
- {doc}`how_it_works` - Deep dive into architecture and patterns
- {doc}`examples` - Browse working examples
- {doc}`api_reference` - API documentation

### Services Documentation

- {doc}`services/component_registry` - ComponentNameRegistry service
- {doc}`services/component_lookup` - ComponentLookup service
- {doc}`services/middleware` - MiddlewareManager service

## Contents

```{toctree}
:maxdepth: 2

getting_started
core_concepts
how_it_works
services/component_registry
services/component_lookup
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
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable

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
```

Components are automatically discovered, dependencies are injected, and you can reference them by name in templates.

## Next Steps

1. Follow the {doc}`getting_started` guide to set up your first application
2. Read {doc}`core_concepts` to understand the fundamental concepts
3. Explore {doc}`examples` for real-world patterns
4. Dive into {doc}`how_it_works` for advanced topics
