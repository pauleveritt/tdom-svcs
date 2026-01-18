# tdom-svcs Project Guidelines

## Project Overview

tdom-svcs is an integration library that provides seamless dependency injection between tdom (Template DOM for Python 3.14 t-strings) and svcs (service container). It enables automatic service injection into template components while keeping the core tdom library minimal and dependency-free.

## Core Policies

### Component Type Policy

#### Class Components (Dataclasses)
- **CAN** use `Inject[]` for dependency injection
- **CAN** be registered by string name in ComponentNameRegistry
- **CAN** be discovered via `@injectable` decorator and `scan_components()`
- **CAN** be resolved via ComponentLookup by string name
- **MUST** use **HopscotchInjector** in all examples and production code

#### Function Components
- **CAN** use `Inject[]` for dependency injection
- **CANNOT** be registered by string name in ComponentNameRegistry
- **CANNOT** use `@injectable` decorator (svcs-di enforces this)
- **CANNOT** be discovered via `scan_components()`
- **CANNOT** be resolved via ComponentLookup by string name
- **SHOULD** use **KeywordInjector** in educational examples only

### Injector Usage Policy

#### HopscotchInjector (Primary - Production Use)
- **USE FOR:** All class components, ComponentLookup integration, production patterns
- **SUPPORTS:** Resource-based resolution (`resource=X`), location-based resolution (`location=PurePath`)
- **REQUIRED FOR:** Any example using ComponentLookup or `@injectable` metadata
- **DEFAULT:** This is the primary injector for tdom-svcs

**Import:**
```python
from svcs_di.injectors.hopscotch import HopscotchInjector, HopscotchAsyncInjector
```

#### KeywordInjector (Educational Only)
- **USE FOR:** Simple function component examples with direct injection
- **USE WHEN:** No ComponentLookup or string name resolution needed
- **LIMITATIONS:** No resource/location resolution, no multi-implementation support
- **ONLY FOR:** Educational examples showing basic `Inject[]` with functions

**Import:**
```python
from svcs_di.injectors.keyword import KeywordInjector, KeywordAsyncInjector
```

**CRITICAL:** ComponentLookup MUST use HopscotchInjector, never KeywordInjector, because it requires resource and location-based resolution capabilities.

## Example Structure Guidelines

### Directory Structure

Each example should be in its own directory with the following structure:

```
examples/
└── example-name/
    ├── README.md              # Example overview and key concepts
    ├── app.py                 # Registry setup, scanning, container creation
    ├── site.py                # Example-specific logic (requests, rendering)
    ├── components/            # All component classes
    │   ├── __init__.py
    │   ├── button.py
    │   └── dashboard.py
    └── services/              # All service classes
        ├── __init__.py
        ├── database.py
        └── auth.py
```

### File Responsibilities

#### `app.py` - Application Setup (Reusable Pattern)

This file contains the standard setup that's similar across examples:

```python
"""Application setup: registry, scanning, and container creation."""

import svcs
from svcs_di.injectors.hopscotch import HopscotchInjector

from tdom_svcs import ComponentNameRegistry, scan_components
from tdom_svcs.services.component_lookup import ComponentLookup


def setup_application() -> tuple[svcs.Registry, svcs.Container]:
    """
    Set up the application with dependency injection.

    Returns:
        Tuple of (registry, container) ready for use.
    """
    # Create svcs registry and component name registry
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()

    # Scan packages for @injectable components
    # This registers components in both registries
    scan_components(
        registry,
        component_registry,
        "components",  # Relative import from example directory
        "services",    # Services may also be components
    )

    # Register services (non-component dependencies)
    from services.database import DatabaseService
    from services.auth import AuthService

    registry.register_value(DatabaseService, DatabaseService())
    registry.register_value(AuthService, AuthService())

    # Register the component name registry itself
    registry.register_value(ComponentNameRegistry, component_registry)

    # Register injector (use HopscotchInjector for production)
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    # Register ComponentLookup service
    def component_lookup_factory(container: svcs.Container) -> ComponentLookup:
        return ComponentLookup(container=container)

    registry.register_factory(ComponentLookup, component_lookup_factory)

    # Create container
    container = svcs.Container(registry)

    return registry, container


if __name__ == "__main__":
    # This allows testing the setup independently
    registry, container = setup_application()
    print(f"✓ Application setup complete")
    print(f"✓ Registry configured with services and components")
    print(f"✓ Container ready for requests")
```

**Key Points:**
- Returns `(registry, container)` tuple for use by `site.py`
- Uses `HopscotchInjector` (production standard)
- Registers `ComponentNameRegistry`, injector, and `ComponentLookup`
- Scans `components/` and `services/` packages
- Registers service instances or factories
- Can be run independently to verify setup

#### `site.py` - Example-Specific Logic

This file contains the unique aspects of the example:

```python
"""Example-specific demonstration code."""

from app import setup_application


def simulate_request(container, user_id: int = 1):
    """
    Simulate processing a request with the container.

    Args:
        container: The svcs container with all services registered
        user_id: User ID for this request
    """
    from tdom_svcs.services.component_lookup import ComponentLookup

    # Get ComponentLookup service
    lookup = container.get(ComponentLookup)

    # Resolve and render components
    button = lookup("Button", context={})
    dashboard = lookup("Dashboard", context={"user_id": user_id})

    # In a real app, these would be called/rendered
    print(f"✓ Resolved Button component: {button}")
    print(f"✓ Resolved Dashboard component: {dashboard}")

    # Example-specific operations
    if hasattr(dashboard, "render"):
        result = dashboard.render()
        print(f"Dashboard output: {result}")


def main():
    """Run the example."""
    print("=" * 60)
    print("Example: Component Discovery and Registration")
    print("=" * 60)

    # Setup application (standardized in pure_tdom.py)
    registry, container = setup_application()

    # Example-specific demonstration
    print("\n--- Simulating Request ---")
    simulate_request(container, user_id=123)

    print("\n✓ Example complete!")


if __name__ == "__main__":
    main()
```

**Key Points:**
- Imports `setup_application()` from `app.py`
- Contains example-specific demonstration logic
- Shows how to use ComponentLookup
- Simulates request processing
- Demonstrates the unique aspects of this example
- Should be the main entry point (`python -m examples.example-name.site`)

#### `components/` - Component Classes

Each component in its own file:

```python
# components/button.py
"""Button component."""

from dataclasses import dataclass

from svcs_di import Inject
from svcs_di.injectors.decorators import injectable


@injectable
@dataclass
class Button:
    """
    Simple button component with dependency injection.

    This component will be discovered by scan_components() and registered
    as "Button" in ComponentNameRegistry.
    """

    label: str
    db: Inject["DatabaseService"]  # Injected dependency

    def render(self) -> str:
        """Render the button."""
        user = self.db.get_user(1)
        return f'<button>{self.label} - User: {user["name"]}</button>'
```

**Key Points:**
- One component per file (better organization)
- Always use `@injectable` decorator for class components
- Use `Inject[]` for service dependencies
- Include docstring explaining the component
- Component name derived from class name (`Button` -> "Button")

#### `components/__init__.py` - Component Exports

```python
"""Component package exports."""

from .button import Button
from .dashboard import Dashboard

__all__ = ["Button", "Dashboard"]
```

#### `services/` - Service Classes

Each service in its own file:

```python
# services/database.py
"""Database service."""


class DatabaseService:
    """Example database service for dependency injection."""

    def __init__(self):
        """Initialize with mock data."""
        self._users = {
            1: {"id": 1, "name": "Alice", "role": "admin"},
            2: {"id": 2, "name": "Bob", "role": "user"},
        }

    def get_user(self, user_id: int) -> dict:
        """Get user by ID."""
        return self._users.get(user_id, {"id": user_id, "name": "Unknown"})
```

**Key Points:**
- Services are NOT components (no `@injectable` unless used as components)
- Registered in `app.py` via `registry.register_value()` or `registry.register_factory()`
- Can be injected into components via `Inject[]`
- Contain business logic, not rendering logic

#### `services/__init__.py` - Service Exports

```python
"""Service package exports."""

from .auth import AuthService
from .database import DatabaseService

__all__ = ["AuthService", "DatabaseService"]
```

#### `README.md` - Example Documentation

```markdown
# Example: Component Discovery and Registration

This example demonstrates automatic component discovery using `@injectable` decorator and `scan_components()`.

## Key Concepts

- `@injectable` decorator marks components for discovery
- `scan_components()` finds and registers components
- `ComponentLookup` resolves components by string name
- `Inject[]` enables automatic dependency injection
- `HopscotchInjector` provides production-ready resolution

## Structure

- `app.py` - Standard application setup
- `site.py` - Example-specific demonstration
- `components/` - Component classes with `@injectable`
- `services/` - Service classes for dependency injection

## Running

\`\`\`bash
python -m examples.component-discovery.site
\`\`\`

## What You'll Learn

1. How to mark components with `@injectable`
2. How to scan packages for components
3. How ComponentLookup resolves components by name
4. How dependencies are automatically injected
```

### Example Categories

#### Basic Examples
- **component-discovery** - Basic `@injectable` and `scan_components()`
- **function-components** - Simple functions with `Inject[]` (uses KeywordInjector)
- **class-components** - Class components with `Inject[]` (uses HopscotchInjector)

#### Advanced Examples
- **resource-based** - Components with `@injectable(resource=X)`
- **location-based** - Components with `@injectable(location=PurePath)`
- **multi-implementation** - Multiple implementations selected by context

#### Integration Examples
- **tdom-integration** - Full tdom template rendering with components
- **async-components** - Async components with `HopscotchAsyncInjector`
- **middleware** - Component lifecycle middleware hooks

### Running Examples

Examples should be runnable as modules:

```bash
# Run the site.py (main entry point)
python -m examples.component-discovery.site

# Or run pure_tdom.py to verify setup
python -m examples.component-discovery.app
```

### Example Testing

Each example should be testable:

```python
# examples/component-discovery/test_example.py
"""Test the component discovery example."""

import pytest
from examples.component_discovery.app import setup_application


def test_setup_application():
    """Test that application setup works correctly."""
    registry, container = setup_application()

    from tdom_svcs.services.component_lookup import ComponentLookup

    # Verify ComponentLookup is available
    lookup = container.get(ComponentLookup)
    assert lookup is not None

    # Verify components are registered
    button = lookup("Button", context={})
    assert button is not None
```

## Code Style Guidelines

### Type Hints
- Use `Inject[ServiceType]` for dependency injection
- Use forward references for circular dependencies: `Inject["ServiceType"]`
- Always type hint function parameters and return values

### Dataclasses
- Use `@dataclass` for component classes
- Use `frozen=False` (default) for mutable components
- Use `frozen=True` for immutable components (post-render Nodes)

### Imports
- Group imports: standard library, third-party, local
- Use absolute imports for clarity
- Use `from X import Y` for commonly used items

### Documentation
- Every component needs a docstring
- Every service needs a docstring
- Explain what the component/service does and why
- Document injected dependencies in docstring

### Component Names
- Component string names derived from `class.__name__`
- No custom name override mechanism
- Use clear, descriptive class names (e.g., `Button`, not `Btn`)

## Testing Guidelines

### Unit Tests
- Test components in isolation with mock services
- Use `HopscotchInjector` in tests (production injector)
- Test service injection works correctly
- Test component registration and lookup

### Integration Tests
- Test complete workflow: setup → scan → resolve → render
- Test ComponentLookup integration
- Test resource and location-based resolution
- Verify all services are injected correctly

### Example Tests
- Each example should have a `test_example.py`
- Test that `setup_application()` works
- Test that components can be resolved
- Don't test implementation details, test behavior

## Documentation Standards

### Module Docstrings
```python
"""
Module name and purpose.

Longer description of what this module provides and how it fits
into the overall system. Explain key concepts and usage patterns.
"""
```

### Class Docstrings
```python
@injectable
@dataclass
class Button:
    """
    Simple button component with dependency injection.

    This component demonstrates basic dependency injection using Inject[].
    It will be discovered by scan_components() and registered as "Button"
    in ComponentNameRegistry.

    Attributes:
        label: The button label text
        db: Injected database service
    """
```

### Function Docstrings
```python
def setup_application() -> tuple[svcs.Registry, svcs.Container]:
    """
    Set up the application with dependency injection.

    This function creates and configures the svcs registry, scans for
    components, and returns a ready-to-use container.

    Returns:
        Tuple of (registry, container) ready for processing requests.
    """
```

## Common Patterns

### Registering Services
```python
# Value registration (singleton instance)
registry.register_value(DatabaseService, DatabaseService())

# Factory registration (new instance per request)
registry.register_factory(AuthService, AuthService)

# Factory with dependencies
def create_service(container: svcs.Container) -> MyService:
    db = container.get(DatabaseService)
    return MyService(db)

registry.register_factory(MyService, create_service)
```

### Using ComponentLookup
```python
# Get ComponentLookup from container
lookup = container.get(ComponentLookup)

# Resolve component by string name
component = lookup("Button", context={"user_id": 123})

# Component is constructed with all dependencies injected
result = component.render()
```

### Resource-Based Components
```python
@injectable(resource=AdminContext)
@dataclass
class AdminDashboard:
    """Dashboard for admin users."""
    auth: Inject[AuthService]

# Only resolves when AdminContext is in container
```

### Location-Based Components
```python
from pathlib import PurePath

@injectable(location=PurePath("/admin"))
@dataclass
class AdminPanel:
    """Admin panel for /admin routes."""

# Only resolves at /admin location
```

## Anti-Patterns to Avoid

### ❌ Using KeywordInjector for Class Components
```python
# WRONG - Use HopscotchInjector for class components
registry.register_factory(KeywordInjector, KeywordInjector)
```

### ❌ Registering Function Components by Name
```python
# WRONG - Functions cannot be registered by string name
def my_button(label: str, db: Inject[DatabaseService]):
    return f"<button>{label}</button>"

# This should not be done
component_registry.register("MyButton", my_button)
```

### ❌ Using ComponentLookup with KeywordInjector
```python
# WRONG - ComponentLookup requires HopscotchInjector
registry.register_factory(KeywordInjector, KeywordInjector)
lookup = ComponentLookup(container)  # Will fail on resource/location components
```

### ❌ Single-File Examples
```python
# WRONG - Don't put everything in one file
# examples/bad_example.py

class Service: ...
@injectable
class Component: ...
def setup(): ...
def main(): ...
```

Use the directory structure instead.

### ❌ Missing Exports in __init__.py
```python
# WRONG - Don't forget __init__.py and __all__
# This breaks scan_components()
```

Always create `__init__.py` with `__all__` exports.

## Migration from Old Example Format

### Old Format (Single File)
```python
# examples/old_example.py
class DatabaseService: ...
@injectable
class Button: ...
def main(): ...
```

### New Format (Directory Structure)
```
examples/old-example/
├── README.md
├── app.py              # setup_application()
├── site.py             # main() moved here
├── components/
│   ├── __init__.py
│   └── button.py       # Button moved here
└── services/
    ├── __init__.py
    └── database.py     # DatabaseService moved here
```

## Questions to Ask

When creating a new example, ask:

1. **What injector?** If using ComponentLookup or class components → HopscotchInjector
2. **What's the unique aspect?** Put it in `site.py`, keep `app.py` standard
3. **What components?** One per file in `components/`
4. **What services?** One per file in `services/`
5. **What's the README?** Explain the key concepts being demonstrated
6. **Is it testable?** Add `test_example.py` to verify it works

## Review Checklist

Before committing an example:

- [ ] Directory structure follows guidelines (`app.py`, `site.py`, `components/`, `services/`)
- [ ] Uses `HopscotchInjector` (unless educational function example)
- [ ] All components have `@injectable` decorator
- [ ] All components use `Inject[]` for dependencies
- [ ] Services registered in `app.py`
- [ ] README.md explains the example
- [ ] Can run with `python -m examples.example-name.site`
- [ ] Has test file: `test_example.py`
- [ ] All files have docstrings
- [ ] Follows component type policy (classes for name lookup)
- [ ] No anti-patterns present
