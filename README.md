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
from dataclasses import dataclass
from svcs_di import HopscotchContainer, HopscotchRegistry, Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import scan


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
registry = HopscotchRegistry()

# Register services
registry.register_value(DatabaseService, DatabaseService())

# Scan for components
scan(registry, "app.components")

# Create container and resolve components with inject()
with HopscotchContainer(registry) as container:
    # Resolve component with automatic dependency injection
    button = container.inject(Button)
    output = button()  # <button>Click</button>
```

## Key Concepts

### Class vs Function Components

- **Class components** use the `@injectable` decorator and can be registered for DI
- **Function components** can use `Inject[]` but are best called directly with an injector

### Container and Registry

- **HopscotchRegistry** - Extended registry with `register_implementation()` for multi-implementation support
- **HopscotchContainer** - Extended container with built-in `inject()` and `ainject()` methods

### Injector Selection

- **HopscotchContainer.inject()** (production) - Built-in DI with resource/location resolution
- **KeywordInjector** (educational) - Simple cases, function components only

## Context and Config

The `html()` function accepts optional `context` and `config` parameters that are automatically passed to components that declare them.

### Passing Context and Config

```python
from tdom_svcs import html

# Pass context (any value - dict, object, or DI container)
result = html(t"<{MyComponent} />", context={"user": "Alice"})

# Pass config (any value)
result = html(t"<{MyComponent} />", config=app_settings)

# Pass both
result = html(t"<{MyComponent} />", context=ctx, config=cfg)
```

### What They Represent

| Parameter | Purpose | Typical Values |
|-----------|---------|----------------|
| `context` | Runtime state passed through the component tree | Dict, request object, or `HopscotchContainer` for DI |
| `config`  | Application configuration | Settings object, feature flags |

### How Components Receive Them

Components declare `context` and/or `config` parameters to receive them:

**Function components:**
```python
from tdom import Node
from tdom_svcs import html

def Dashboard(context: dict | None = None) -> Node:
    user = context.get("user", "Unknown") if context else "Unknown"
    return html(t'<div class="dashboard">Hello {user}!</div>')

# Usage
result = html(t"<{Dashboard} />", context={"user": "Alice"})
```

**Class components:**
```python
@dataclass
class Dashboard:
    title: str = "Dashboard"

    def __call__(self, context: dict | None = None) -> Node:
        user = context.get("user", "Unknown") if context else "Unknown"
        return html(t'<div>{self.title}: Hello {user}!</div>')
```

### Context with Dependency Injection

When `context` is a `HopscotchContainer`, components with `Inject[]` fields automatically get dependencies injected:

```python
@dataclass
class Dashboard:
    db: Inject[DatabaseService]  # Automatically injected from context

    def __call__(self) -> Node:
        user = self.db.get_current_user()
        return html(t'<div>Hello {user}!</div>')

# Usage with DI container
with HopscotchContainer(registry) as container:
    result = html(t"<{Dashboard} />", context=container)
```

### Nested Components

Context and config are passed through the entire component tree:

```python
def Header(context=None):
    user = context.get("user") if context else "Guest"
    return html(t"<header>Welcome {user}</header>")

def Page(context=None, children=()):
    return html(t"<main><{Header} />{children}</main>", context=context)

# Both Header and Page receive the same context
result = html(t"<{Page}><p>Content</p></{Page}>", context={"user": "Alice"})
```

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
