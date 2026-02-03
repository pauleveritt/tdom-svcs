# tdom-svcs

Allow a `context` to be passed down the `tdom` call chain, with optional support for `svcs-di` dependency injection.

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

## tdom and Context

Prop drilling—passing data through multiple component layers—is a common pain point in component-based architectures. A
deeply nested component needs some value, so every component in the chain must accept and forward it.

This package is a fork of [tdom](https://github.com/pauleveritt/tdom) that adds an optional `context` argument to the
`html()` function. The context flows automatically through the component tree. (The goal is to contribute this upstream
to tdom.)

Context is simply a mapping. Pass it at the top level:

```python
from tdom_svcs import html

result = html(t"<{Page} />", context={"user": "Alice", "theme": "dark"})
```

Components can request `context` as a parameter, similar to how they request `children`:

```python
def Header(context=None):
    user = context.get("user", "Guest") if context else "Guest"
    return html(t"<header>Welcome, {user}!</header>")


def Page(context=None):
    # Header automatically receives the same context
    return html(t"<main><{Header} /><p>Content here</p></main>", context=context)
```

The nested `Header` component gets the context without `Page` explicitly passing `user` as a prop.

See the [pure_tdom](examples/basic/pure_tdom.py)
and [function_dataclass_poco](examples/basic/function_dataclass_poco.py) examples for more.

## Using with svcs

When `context` is an `svcs.Container` (which has a mapping interface), special behavior is enabled. Component fields
using `Inject[ServiceType]` are automatically resolved from the container:

```python
@dataclass
class Dashboard:
    db: Inject[DatabaseService]  # Automatically injected from context

    def __call__(self) -> Node:
        user = self.db.get_current_user()
        return html(t"<div>Hello, {user}!</div>")
```

This is built on [svcs-di](https://github.com/pauleveritt/svcs-di), which adds conveniences like decorators and package
scanning:

```python
from svcs_di import HopscotchRegistry, HopscotchContainer
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import scan

registry = HopscotchRegistry()
scan(registry, "myapp.components")  # Discover @injectable classes

with HopscotchContainer(registry) as container:
    result = html(t"<{Dashboard} />", context=container)
```

Beyond basic DI, svcs-di enables:

- **Component overrides** - Replace a component without changing templates:

```python
# Site overrides app's Greeting with a French version
@injectable(for_=Greeting)
class FrenchGreeting(Greeting):
    def __call__(self) -> Node:
        return html(t"<h1>Bonjour!</h1>")
```

- **Resource-based variation** - Different components based on content type:

```python
# Use a special heading for BlogPost resources
@injectable(for_=Heading, resource=BlogPost)
class BlogHeading(Heading):
    ...
```

- **Location-based variation** - Different components based on URL path:

```python
# French version when URL starts with /fr/
@injectable(for_=Greeting, location="/fr/")
class FrenchGreeting(Greeting):
    ...
```

See the [basic_container](examples/hopscotch/basic_container.py), [override](examples/hopscotch/override/),
and [location](examples/hopscotch/location/) examples.

## Middleware

Middleware intercepts component processing for cross-cutting concerns. Each middleware receives the component, its
props, and the context—then returns modified props (or `None` to halt rendering).

Middleware can be **global** (runs for all components) or **per-component** (attached to specific components).
Middleware can also inject services to help do their job.

Use cases include validation, logging, and asset collection:

```python
@middleware
@dataclass
class HtmlValidator:
    validator: Inject[ValidatorService]  # Injected service
    priority: int = 100  # Runs late, after rendering

    def __call__(self, component, props, context):
        # Validate HTML output for accessibility
        self.validator.check(props.get("result"))
        return props
```

```python
@middleware
@dataclass
class AssetRewriter:
    assets: Inject[AssetService]
    priority: int = 50

    def __call__(self, component, props, context):
        # Rewrite static asset paths for CDN
        if "src" in props:
            props["src"] = self.assets.cdn_url(props["src"])
        return props
```

See the [aria](examples/middleware/aria/), [path](examples/middleware/path/),
and [dependencies](examples/middleware/dependencies/) examples.

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

## Documentation

Full documentation is available at [docs/](docs/):

- [Getting Started](docs/getting_started.md) - Installation and first component
- [Core Concepts](docs/core_concepts.md) - Components, DI, and registries
- [The Node Standard](docs/node.md) - Ecosystem interoperability
- [How It Works](docs/how_it_works.md) - Architecture and patterns
- [Middleware](docs/services/middleware.md) - Lifecycle hooks
- [Examples](docs/examples/index.md) - Working code examples
- [API Reference](docs/api_reference.md) - API documentation

## Testing

```bash
# Run tests
uv run pytest

# Run tests in parallel
uv run pytest -n auto

# Run with coverage
uv run pytest --cov=tdom_svcs

# Type check
uv run ty check

# Lint and format
uv run ruff check .
uv run ruff format .
```
