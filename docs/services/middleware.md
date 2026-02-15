# Middleware

The **middleware system** in tdom-svcs is powered by [svcs-di's middleware framework](https://github.com/hynek/svcs-di). tdom-svcs re-exports all middleware symbols and adds tdom-specific middleware for working with Node trees.

## Generic Middleware (from svcs-di)

All core middleware functionality comes from svcs-di:

```python
from tdom_svcs import (
    middleware,           # Decorator for global middleware
    hookable,            # Decorator for targets with middleware hooks
    execute_middleware,  # Execute global middleware chain
    execute_target_middleware,  # Execute per-target middleware
    register_middleware, # Imperative registration
    register_hookable,   # Register hookable targets
)
```

For complete middleware documentation, see the [svcs-di middleware guide](https://github.com/hynek/svcs-di).

## tdom-Specific Middleware

tdom-svcs provides middleware for operating on rendered Node trees:

### Path Collection Middleware

Tracks component locations and asset references during rendering:

```python
from tdom_svcs.services import PathCollector, PathMiddleware

# PathMiddleware records paths to components and assets
# Useful for build systems, static analysis, etc.
```

See `examples/middleware/path/` for a complete example.

### ARIA/Accessibility Middleware

Inspects rendered Node trees for accessibility issues:

```python
from aria_testing import query_all_by_tag_name
from svcs_di import Inject, injectable
from svcs_di.middleware import Props, PropsResult, Target
from typing import Any

@injectable
class AriaVerifierMiddleware:
    """Warns about missing alt attributes on images."""

    logger: Inject[Logger]
    priority: int = 10

    def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
        # Render target and inspect Node tree
        node = self._render(target)
        images = query_all_by_tag_name(node, "img")

        for img in images:
            if "alt" not in img.attrs:
                self.logger.warn(f"{target.__name__}: missing alt")

        return props
```

This pattern works for any Node tree analysis:
- Link validation
- Security scanning
- i18n injection
- Tree optimization

See `examples/middleware/aria/` for a complete example.

## Usage with tdom

Middleware integrates with tdom's rendering system:

```python
from svcs_di.injectors import HopscotchRegistry, HopscotchContainer
from tdom_svcs import scan, html

# Scan discovers @middleware and @hookable
registry = HopscotchRegistry()
scan(registry, "myapp.middleware", "myapp.components")

# Container provides context for middleware execution
with HopscotchContainer(registry) as container:
    # Global middleware runs automatically during html() processing
    result = html(t"<{MyComponent} />", context=container)
```

## See Also

- [svcs-di middleware documentation](https://github.com/hynek/svcs-di) - Complete middleware reference
- {doc}`../examples/middleware/index` - tdom-specific middleware examples
- {doc}`../how_it_works` - Architecture overview
