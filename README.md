# tdom-svcs

TDOM rendering with optional `svcs` dependency injection for component trees.

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
- **tstring-html / tdom**
- **svcs**

## tdom and Containers

Prop drilling—passing data through multiple component layers—is a common pain point in component-based architectures. A
deeply nested component needs some value, so every component in the chain must accept and forward it.

tdom-svcs keeps the plain rendering path first and adds an optional `svcs`
container path for dependency-aware components.

The plain rendering path is still the contract. Import `html`, render a
template, and add a container only when the component tree needs it:

```python
from tdom_svcs import html

result = html(t"<h1>Hello, Alice!</h1>")
```

Dependency injection is an additive path for larger applications, not a
prerequisite for rendering HTML.

Plain components can compose without setup:

```python
from tdom_svcs import html

def Header():
    return t"<header>Welcome!</header>"


def Page():
    return t"<main><{Header} /><p>Content here</p></main>"


result = html(t"<{Page} />")
```

The nested `Header` component renders without `Page` explicitly calling it or
passing setup objects through the tree.

See the [pure_tdom](examples/basic/pure_tdom.py)
and [function_dataclass_poco](examples/basic/function_dataclass_poco.py) examples for more.

## Using with svcs

When `container` is an `svcs.Container`, component fields using
`Inject[ServiceType]` are automatically resolved from the container:

```python
from dataclasses import dataclass

from svcs_di import Inject

@dataclass
class Dashboard:
    db: Inject[DatabaseService]  # Automatically injected from the container

    def __call__(self):
        user = self.db.get_current_user()
        return t"<div>Hello, {user}!</div>"
```

This is built on [svcs-di](https://github.com/pauleveritt/svcs-di), which adds conveniences like decorators and package
scanning:

```text
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry, injectable

registry = HopscotchRegistry()
scan(registry, "myapp.components")  # Discover @injectable classes

with HopscotchContainer(registry) as container:
    result = html(t"<{Dashboard} />", container=container)
```

Beyond basic DI, svcs-di enables:

- **Component overrides** - Replace a component without changing templates:

```text
# Site overrides app's Greeting with a French version
@injectable(for_=Greeting)
class FrenchGreeting(Greeting):
    def __call__(self):
        return t"<h1>Bonjour!</h1>"
```

- **Resource-based variation** - Different components based on content type:

```text
# Use a special heading for BlogPost resources
@injectable(for_=Heading, resource=BlogPost)
class BlogHeading(Heading):
    ...
```

- **Location-based variation** - Different components based on URL path:

```text
# French version when URL starts with /fr/
@injectable(for_=Greeting, location="/fr/")
class FrenchGreeting(Greeting):
    ...
```

See the [basic_container](examples/hopscotch/basic_container.py), [override](examples/hopscotch/override/),
and [location](examples/hopscotch/location/) examples.

## Middleware

tdom-svcs middleware is powered by [svcs-di's middleware framework](https://github.com/hynek/svcs-di). Each middleware receives the target, its props, and the context—then returns modified props (or `None` to halt execution).

tdom-svcs adds **tdom-specific middleware** for operating on rendered component
output:

```text
from typing import Any

from svcs_di import Inject
from tdom_svcs import Props, PropsResult, Target, middleware

@middleware
@dataclass
class AriaValidator:
    logger: Inject[Logger]
    priority: int = 10

    def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
        # Render target and inspect output for accessibility
        output = self._render(target)
        # Check for missing alt attributes, etc.
        return props
```

Use cases include:
- **Accessibility checking** - Inspect rendered output for ARIA issues
- **Link validation** - Verify internal links point to valid routes

See the [aria](examples/middleware/aria/) example.

## Quick Start

```python
from dataclasses import dataclass

from svcs_di import Inject
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs import html


class DatabaseService:
    def get_button_config(self) -> str:
        return "primary"


# Define a component with dependency injection
@dataclass
class Button:
    db: Inject[DatabaseService]  # Automatically injected
    label: str = "Click"  # Regular parameter

    def __call__(self):
        config = self.db.get_button_config()
        return t'<button class="{config}">{self.label}</button>'


# Setup application
registry = HopscotchRegistry()

# Register services
registry.register_value(DatabaseService, DatabaseService())

with HopscotchContainer(registry) as container:
    output = html(t"<{Button} />", container=container)
    assert output == '<button class="primary">Click</button>'
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
