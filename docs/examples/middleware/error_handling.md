# Error Handling Middleware

This example demonstrates patterns for handling errors gracefully: exception catching, fallback rendering, and the
circuit breaker pattern.

```{note}
This example uses Hopscotch patterns (`@middleware`, `scan()`) for convenience.
You can also use imperative registration with `register_middleware()` if preferred.
```

## Project structure

```
error_handling/
├── app.py              # Main entry point
├── components.py       # FailingComponent for error demos
└── middleware.py       # ErrorHandler, Fallback, CircuitBreaker
```

## Defining middleware with decorators

Middleware classes are marked with the `@middleware` decorator:

```{literalinclude} ../../../examples/middleware/error_handling/middleware.py
:start-after: The circuit breaker middleware
:end-at: class CircuitBreakerMiddleware:
:emphasize-lines: 1
```

The `@middleware` decorator both marks the class for discovery by `scan()` and makes it injectable for DI resolution.

## Circuit breaker pattern

The CircuitBreakerMiddleware implements fail-fast behavior after repeated failures:

```{literalinclude} ../../../examples/middleware/error_handling/middleware.py
:start-at: class CircuitBreakerMiddleware:
:end-at: return props
:emphasize-lines: 13-16
```

After exceeding the failure threshold, all subsequent requests immediately return `None`.

## Fallback middleware

FallbackMiddleware provides default values for missing props. Priority `-5` ensures it runs early:

```{literalinclude} ../../../examples/middleware/error_handling/middleware.py
:start-at: class FallbackMiddleware:
:end-at: return props
:emphasize-lines: 12-14
```

## Error handling middleware

ErrorHandlingMiddleware catches validation errors. High priority (100) ensures it runs late:

```{literalinclude} ../../../examples/middleware/error_handling/middleware.py
:start-at: class ErrorHandlingMiddleware:
:end-at: return None
:emphasize-lines: 18-21
```

## Scanning and setup

The `scan()` function discovers both `@injectable` services and `@middleware` classes:

```{literalinclude} ../../../examples/middleware/error_handling/app.py
:start-at: registry = HopscotchRegistry
:end-at: scan(registry, middleware)
```

## Configuring middleware instances

Get middleware from the container to allow assertions later:

```{literalinclude} ../../../examples/middleware/error_handling/app.py
:start-at: circuit_breaker = container.get
:end-at: error_handler.fallback_props
```

## Running the example

```bash
uv run python -m examples.middleware.error_handling.app
```

Output:

```
<div>Simple Component</div>
```

The example uses assertions to verify behavior. All middleware logic is tested silently.

## Full source code

### `app.py`

```{literalinclude} ../../../examples/middleware/error_handling/app.py
```

### `middleware.py`

```{literalinclude} ../../../examples/middleware/error_handling/middleware.py
```

### `components.py`

```{literalinclude} ../../../examples/middleware/error_handling/components.py
```
