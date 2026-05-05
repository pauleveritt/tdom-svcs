# Middleware

The **middleware system** in tdom-svcs is powered by [svcs-di's middleware framework](https://github.com/hynek/svcs-di). tdom-svcs re-exports all middleware symbols and adds tdom-specific middleware for working with rendered component output.

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

tdom-svcs provides middleware for operating on rendered component output:

### ARIA/Accessibility Middleware

Inspects rendered HTML for accessibility issues:

```python
from html.parser import HTMLParser
from svcs_di import Inject, injectable
from svcs_di.middleware import Props, PropsResult, Target
from typing import Any

@injectable
class AriaVerifierMiddleware:
    """Warns about missing alt attributes on images."""

    logger: Inject[Logger]
    priority: int = 10

    def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
        # Render target and inspect HTML
        output = self._render(target)
        images = parse_img_tags(output)

        for img in images:
            if "alt" not in img.attrs:
                self.logger.warn(f"{target.__name__}: missing alt")

        return props
```

This pattern works for output analysis such as:
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
    result = html(t"<{MyComponent} />", container=container)
```

## See Also

- [svcs-di middleware documentation](https://github.com/hynek/svcs-di) - Complete middleware reference
- {doc}`../examples/middleware/index` - tdom-specific middleware examples
- {doc}`../how_it_works` - Architecture overview
