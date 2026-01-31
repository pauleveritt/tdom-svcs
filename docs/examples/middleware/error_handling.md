# Error Handling Middleware

This example demonstrates patterns for handling errors gracefully: exception catching, fallback rendering, and the circuit breaker pattern.

## Project structure

```
error_handling/
├── app.py              # Main entry point
├── components.py       # Greeting, FailingComponent
├── services.py         # Database, Users services
├── middleware.py       # ErrorHandler, Fallback, CircuitBreaker
├── request.py          # Request dataclass
└── site/
    └── __init__.py     # Site configuration placeholder
```

## Error handling middleware

The ErrorHandlingMiddleware catches validation errors and can either halt or provide fallback props:

```{literalinclude} ../../../examples/middleware/error_handling/middleware.py
:start-at: class ErrorHandlingMiddleware
:end-at: return None
```

Note the high priority (100) which ensures this middleware runs late in the chain, after other middleware have had a chance to process.

## Fallback middleware

FallbackMiddleware provides default values for missing props:

```{literalinclude} ../../../examples/middleware/error_handling/middleware.py
:start-at: class FallbackMiddleware
:end-at: return props
```

With priority -5, it runs early to set defaults before validation occurs.

## Circuit breaker pattern

CircuitBreakerMiddleware implements fail-fast behavior after repeated failures:

```{literalinclude} ../../../examples/middleware/error_handling/middleware.py
:start-at: class CircuitBreakerMiddleware
:end-at: return props
```

After exceeding the failure threshold, all subsequent requests immediately return `None` without processing.

## Using error handling middleware

Register middleware with appropriate priorities:

```{literalinclude} ../../../examples/middleware/error_handling/app.py
:start-at: circuit_breaker = CircuitBreakerMiddleware
:end-at: manager.register_middleware(error_handler)
```

## Running the example

```bash
uv run python -m examples.middleware.error_handling.app
```

Output:
```
<h1>Hello Alice!</h1>
```

The example uses assertions to verify behavior. All middleware logic is tested silently.

## Full source code

### app.py

```{literalinclude} ../../../examples/middleware/error_handling/app.py
```

### middleware.py

```{literalinclude} ../../../examples/middleware/error_handling/middleware.py
```

### components.py

```{literalinclude} ../../../examples/middleware/error_handling/components.py
```
