# Examples

The best way to learn is by example. Below are links to working code demonstrating the various features of `tdom-svcs`.

## Running Examples

All examples can be run directly with Python 3.14+:

```bash
# Using uv (recommended)
uv run python examples/basic/pure_tdom.py
uv run python examples/hopscotch/basic_container.py

# Using python directly
python examples/basic/pure_tdom.py
```

## Basic Examples

Foundational concepts: the `context` argument, component flavors (functions, dataclasses, POCOs), and dependency injection basics.

| Example | Description |
|---------|-------------|
| [pure_tdom.py](../../examples/basic/pure_tdom.py) | Context argument fundamentals with no DI framework |
| [tdom_svcs.py](../../examples/basic/tdom_svcs.py) | Basic tdom with svcs container |
| [function_dataclass_poco.py](../../examples/basic/function_dataclass_poco.py) | Component flavors: functions, dataclasses, POCOs |
| [inject_service.py](../../examples/basic/inject_service.py) | Service-to-service injection |
| [props_priority.py](../../examples/basic/props_priority.py) | Props override patterns with InitVar |

[Browse Basic Examples](basic/index)

## Hopscotch Examples

Advanced features: automatic scanning with `@injectable`, component overrides, and context-aware resolution based on resources and locations.

| Example | Description |
|---------|-------------|
| [basic_container.py](../../examples/hopscotch/basic_container.py) | HopscotchContainer and @injectable |
| [app_site/](../../examples/hopscotch/app_site/) | App/site separation pattern |
| [override/](../../examples/hopscotch/override/) | Component override with register_implementation |
| [scan_decorators/](../../examples/hopscotch/scan_decorators/) | Automatic override discovery with @injectable(for_=) |
| [resource/](../../examples/hopscotch/resource/) | Resource-based component resolution |
| [location/](../../examples/hopscotch/location/) | URL path-based component resolution |

[Browse Hopscotch Examples](hopscotch/index)

## Middleware Examples

Cross-cutting concerns: intercepting and modifying component rendering for logging, caching, and more.

| Example | Description |
|---------|-------------|
| [basic/](../../examples/middleware/basic/) | Chain execution, priority ordering, halting |
| [dependencies/](../../examples/middleware/dependencies/) | Middleware with injected services, testing with fakes |
| [error_handling/](../../examples/middleware/error_handling/) | Exception handling, fallback rendering, circuit breaker |
| [scoping/](../../examples/middleware/scoping/) | Global vs per-component middleware, async support |

[Browse Middleware Examples](middleware/index)

## Node Examples

Node ecosystem compatibility: testing tools like aria-testing. [Browse Node Examples](node/index)

## Common Patterns

### Setup Pattern

All examples follow a consistent setup pattern:

```python
def setup_application() -> svcs.Container:
    """Set up application with all services."""
    registry = svcs.Registry()

    # Register services
    registry.register_value(SomeService, SomeService())

    # Discover components
    scan(registry, __name__)

    # Register injector
    registry.register_factory(HopscotchInjector, HopscotchInjector)

    return svcs.Container(registry)
```

### Component Pattern

All components use the class-based pattern with `@injectable`:

```python
@injectable
@dataclass
class MyComponent:
    """Component with dependencies and parameters."""

    service: Inject[SomeService]  # Injected
    param: str = "default"         # Regular parameter

    def __call__(self) -> str:
        """Render component."""
        data = self.service.get_data()
        return f"<div>{self.param}: {data}</div>"
```

### Middleware Pattern

All middleware follow the middleware protocol:

```python
@dataclass
class MyMiddleware:
    priority: int = 0  # Execution order

    def __call__(self, component, props, context):
        """Process props before component construction."""
        # Modify props, validate, add data, etc.
        return props  # Or None to halt
```

## Learning Path

We recommend exploring examples in this order:

1. **Start with fundamentals:** Basic examples
2. **Learn Hopscotch patterns:** Container, scanning, overrides
3. **Master middleware:** Lifecycle hooks and cross-cutting concerns

## Next Steps

After exploring examples:
- Read {doc}`../how_it_works` for architectural deep dive
- Study {doc}`../services/middleware` for middleware system details

## TODO

- Registered component factories in config, function that requests `context`
- @injectable without scanning
- scan
- Replacement service
- Protocols
- scan inside a test and locals
- Use of aria-testing
- children, config, context

## Hopscotch

- app/site
- HC context manager
- Vary the service
- Vary the component
    - Subtype that just replaces the render
- svcs_registry/svcs_container conventions
- Location
- Resource


```{toctree}
:hidden:
:maxdepth: 2

basic/index
hopscotch/index
middleware/index
node/index
```
