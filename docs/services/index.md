# Services

The services system in tdom-svcs provides foundational functionality for dependency injection, middleware execution, and introspection.

## Overview

tdom-svcs extends the [svcs](https://svcs.hynek.me/) service locator pattern with:

- **Middleware System**: Cross-cutting concerns for component rendering
- **Introspection**: Query and inspect registered services, middleware, and components
- **Path Collection**: Track component locations and static assets during rendering
- **Category System**: Organize and filter services by category tags

## Core Services

### Middleware Manager

The middleware system enables cross-cutting concerns in your application:

```python
from tdom_svcs import register_middleware, execute_middleware

# Register middleware
register_middleware(registry, LoggingMiddleware)
register_middleware(registry, SecurityMiddleware)

# Execute middleware chain
props = execute_middleware(MyComponent, props, container)
```

{doc}`middleware` - Complete middleware documentation

### Registry Introspection

Query your registry to understand what's registered:

```python
from tdom_svcs import list_middlewares, list_components

# List all registered middleware
for info in list_middlewares(registry):
    print(f"{info.middleware_type.__name__}: priority={info.priority}")

# List all registered components
for info in list_components(registry):
    print(f"{info.service_type.__name__}: {len(info.variations)} variations")
```

{doc}`introspection` - Complete introspection documentation

### Path Collection Service

Track component locations and collect static asset references:

```python
from tdom_svcs.services.path import PathCollector

collector = PathCollector()
registry.register_value(PathCollector, collector)

# During rendering, paths are collected
location = collector.register_component(MyComponent)
collector.collect_from_node(rendered_node, location)

# Access collected assets
for asset in collector.assets:
    print(f"Asset: {asset.relative_path} -> {asset.module_path}")
```

See the {doc}`../examples/middleware/index` for path middleware examples.

## Service Patterns

### Service Registration

Register services using svcs patterns:

```python
import svcs
from svcs_di import auto

# Simple value
registry.register_value(Config, Config())

# Factory function
registry.register_factory(Database, lambda: Database())

# Auto-inject dependencies
registry.register_factory(UserService, auto(UserService))
```

### Service Retrieval

Access services from the container:

```python
with svcs.Container(registry) as container:
    # Get a service
    db = container.get(Database)

    # Use in components
    result = html(t"<{MyComponent} />", context=container)
```

### Injectable Services

Use the `@injectable` decorator for automatic registration:

```python
from svcs_di.injectors import injectable
from svcs_di import Inject

@injectable
@dataclass
class UserService:
    db: Inject[Database]

    def get_user(self, user_id: int) -> User:
        return self.db.query(User).get(user_id)
```

## Next Steps

- {doc}`middleware` - Learn about the middleware system
- {doc}`introspection` - Explore registry introspection
- {doc}`../examples/index` - See practical examples

```{toctree}
:maxdepth: 2

middleware
introspection
```
