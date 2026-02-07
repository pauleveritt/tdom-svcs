# Registry Introspection

The introspection module provides helper functions for inspecting registered components and middleware in a `HopscotchRegistry` at runtime. This is useful for debugging, building admin interfaces, and generating documentation.

## Overview

The introspection API provides two main functions:

- **`list_components()`** — Lists all registered component service types with their implementation variations
- **`list_middlewares()`** — Lists all registered global middleware types with their priorities

All return types are frozen dataclasses for immutability and type safety.

## Installation

The introspection helpers are included in the main `tdom-svcs` package:

```python
from tdom_svcs import (
    list_components,
    list_middlewares,
    ComponentInfo,
    ComponentVariation,
    MiddlewareInfo,
)
```

## Basic Usage

### Inspecting Components

```python
from svcs_di.injectors import HopscotchRegistry
from tdom_svcs import list_components

registry = HopscotchRegistry()

# Register some components
class Database:
    pass

class PostgresDB(Database):
    pass

registry.register_implementation(Database, PostgresDB)

# Inspect registered components
components = list_components(registry)

# Access component information
if Database in components:
    info = components[Database]
    print(f"Service type: {info.service_type.__name__}")
    print(f"Number of variations: {len(info.variations)}")

    for variation in info.variations:
        print(f"  Implementation: {variation.implementation.__name__}")
        print(f"  Resource: {variation.resource}")
        print(f"  Location: {variation.location}")
```

### Inspecting Middleware

```python
from dataclasses import dataclass
from tdom_svcs import list_middlewares, middleware, scan

registry = HopscotchRegistry()

# Register middleware
@middleware
@dataclass
class LoggingMiddleware:
    priority: int = -10

    def __call__(self, component, props, context):
        print(f"Processing {component.__name__}")
        return props

scan(registry, locals_dict=locals())

# Inspect registered middleware
middlewares = list_middlewares(registry)

for mw_info in middlewares:
    print(f"Middleware: {mw_info.middleware_type.__name__}")
    print(f"Priority: {mw_info.priority}")
```

## API Reference

### `list_components(registry) -> dict[type, ComponentInfo]`

Lists all registered component services in the registry.

**Parameters:**
- `registry` — `HopscotchRegistry` to inspect

**Returns:**
- Dictionary mapping service types to their `ComponentInfo`
- Returns empty dict if no components are registered

**Example:**
```python
components = list_components(registry)

for service_type, info in components.items():
    print(f"{service_type.__name__}:")
    for variation in info.variations:
        print(f"  - {variation.implementation.__name__}")
```

### `list_middlewares(registry) -> tuple[MiddlewareInfo, ...]`

Lists all registered global middleware types in the registry.

**Parameters:**
- `registry` — `HopscotchRegistry` to inspect

**Returns:**
- Tuple of `MiddlewareInfo` for all registered middleware
- Returns empty tuple if no middleware are registered

**Example:**
```python
middlewares = list_middlewares(registry)

# Sort by priority
sorted_mw = sorted(middlewares, key=lambda m: m.priority or 0)

for mw_info in sorted_mw:
    print(f"{mw_info.middleware_type.__name__} (priority: {mw_info.priority})")
```

### `ComponentInfo`

Frozen dataclass containing complete information about a registered component service type.

**Attributes:**
- `service_type: type` — The service type (interface/protocol) being implemented
- `variations: tuple[ComponentVariation, ...]` — Tuple of all registered implementation variations

**Example:**
```python
info = components[Database]
assert info.service_type is Database
assert isinstance(info.variations, tuple)
assert len(info.variations) > 0
```

### `ComponentVariation`

Frozen dataclass representing a single component implementation variation.

**Attributes:**
- `implementation: type` — The implementation class or factory function
- `resource: type | None` — Optional resource type this variation is specialized for
- `location: PurePath | None` — Optional location path this variation is restricted to

**Example:**
```python
variation = info.variations[0]
print(f"Implementation: {variation.implementation.__name__}")

if variation.resource:
    print(f"Resource-specific for: {variation.resource.__name__}")

if variation.location:
    print(f"Location-specific for: {variation.location}")
```

### `MiddlewareInfo`

Frozen dataclass containing information about a registered global middleware type.

**Attributes:**
- `middleware_type: type[AnyMiddleware]` — The middleware class type
- `priority: int | None` — Middleware execution priority (lower executes first)

**Example:**
```python
mw_info = middlewares[0]
print(f"Type: {mw_info.middleware_type.__name__}")
print(f"Priority: {mw_info.priority}")
```

## Use Cases

### Debugging Registration Issues

Use introspection to verify that components and middleware are registered correctly:

```python
components = list_components(registry)
middlewares = list_middlewares(registry)

print(f"Total components: {len(components)}")
print(f"Total middleware: {len(middlewares)}")

# Check if specific component is registered
if MyComponent not in components:
    print("WARNING: MyComponent not registered!")

# Verify middleware order
sorted_mw = sorted(middlewares, key=lambda m: m.priority or 0)
print("Middleware execution order:")
for mw in sorted_mw:
    print(f"  {mw.priority}: {mw.middleware_type.__name__}")
```

### Building Admin Interfaces

Create admin pages that display registered services:

```python
def admin_services_page(registry):
    """Generate admin page showing all registered services."""
    components = list_components(registry)

    html_parts = ["<h1>Registered Services</h1>"]

    for service_type, info in sorted(components.items(), key=lambda x: x[0].__name__):
        html_parts.append(f"<h2>{service_type.__name__}</h2>")
        html_parts.append("<ul>")

        for variation in info.variations:
            impl_name = variation.implementation.__name__
            resource = f" (resource: {variation.resource.__name__})" if variation.resource else ""
            location = f" (location: {variation.location})" if variation.location else ""
            html_parts.append(f"<li>{impl_name}{resource}{location}</li>")

        html_parts.append("</ul>")

    return "\n".join(html_parts)
```

### Generating Documentation

Automatically generate documentation from registered services:

```python
def generate_service_docs(registry):
    """Generate markdown documentation for all services."""
    components = list_components(registry)

    lines = ["# Service Registry Documentation\n"]

    for service_type, info in sorted(components.items(), key=lambda x: x[0].__name__):
        lines.append(f"## {service_type.__name__}\n")

        if service_type.__doc__:
            lines.append(f"{service_type.__doc__}\n")

        lines.append("### Implementations\n")

        for variation in info.variations:
            impl = variation.implementation
            lines.append(f"- **{impl.__name__}**")

            if variation.resource:
                lines.append(f" — Resource: `{variation.resource.__name__}`")

            if variation.location:
                lines.append(f" — Location: `{variation.location}`")

            lines.append("\n")

    return "\n".join(lines)
```

### Testing Registry Configuration

Verify registry setup in tests:

```python
def test_registry_has_required_services():
    """Ensure all required services are registered."""
    registry = create_production_registry()
    components = list_components(registry)

    required_services = [Database, Cache, EmailService, Logger]

    for service in required_services:
        assert service in components, f"Missing required service: {service.__name__}"

def test_middleware_execution_order():
    """Verify middleware are registered in correct priority order."""
    registry = create_production_registry()
    middlewares = list_middlewares(registry)

    priorities = [m.priority for m in middlewares if m.priority is not None]
    assert priorities == sorted(priorities), "Middleware not in priority order"
```

## Advanced Examples

### Filtering Components by Resource

```python
def get_components_for_resource(registry, resource_type):
    """Get all component variations for a specific resource type."""
    components = list_components(registry)
    result = {}

    for service_type, info in components.items():
        matching_variations = [
            v for v in info.variations
            if v.resource is resource_type
        ]

        if matching_variations:
            result[service_type] = ComponentInfo(
                service_type=service_type,
                variations=tuple(matching_variations)
            )

    return result

# Usage
employee_components = get_components_for_resource(registry, EmployeeContext)
```

### Finding Location-Specific Implementations

```python
from pathlib import PurePath

def get_components_at_location(registry, location):
    """Get all component variations available at a specific location."""
    components = list_components(registry)
    result = {}

    for service_type, info in components.items():
        matching_variations = [
            v for v in info.variations
            if v.location is None or location.is_relative_to(v.location)
        ]

        if matching_variations:
            result[service_type] = ComponentInfo(
                service_type=service_type,
                variations=tuple(matching_variations)
            )

    return result

# Usage
admin_components = get_components_at_location(registry, PurePath("/admin"))
```

### Validating Middleware Configuration

```python
def validate_middleware_configuration(registry):
    """Validate middleware configuration and report issues."""
    middlewares = list_middlewares(registry)
    issues = []

    # Check for missing priorities
    for mw_info in middlewares:
        if mw_info.priority is None:
            issues.append(f"Middleware {mw_info.middleware_type.__name__} has no priority")

    # Check for duplicate priorities
    priorities = [m.priority for m in middlewares if m.priority is not None]
    duplicates = {p for p in priorities if priorities.count(p) > 1}

    if duplicates:
        issues.append(f"Duplicate priorities found: {duplicates}")

    return issues

# Usage
issues = validate_middleware_configuration(registry)
if issues:
    for issue in issues:
        print(f"WARNING: {issue}")
```

## Notes

- All return types are frozen dataclasses and cannot be modified
- The `variations` tuple in `ComponentInfo` maintains LIFO order (most recent registration first)
- Middleware priority extraction only works for dataclass-based middleware with a `priority` field
- Introspection is read-only and does not modify registry state
- For container-specific state, use the container's methods directly (registry-level introspection only)

## See Also

- {doc}`middleware` — Middleware system and registration patterns
- {doc}`../core_concepts` — Component concepts and architecture
- {doc}`../categories` — Category system for organizing services
- [svcs-di documentation](https://github.com/hynek/svcs-di) — Upstream dependency injection library
