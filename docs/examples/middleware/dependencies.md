# Middleware with Dependencies

This example demonstrates middleware that depend on services like Logger and MetricsCollector, using `Inject[]` for
automatic dependency injection.

```{note}
This example uses Hopscotch patterns (`@middleware`, `Inject[]`, `scan()`) for convenience.
You can also use imperative registration with `register_middleware()` if preferred.
```

## Project structure

```
dependencies/
├── app.py              # Main entry point
├── services.py         # Logger, MetricsCollector services
└── middleware.py       # LoggingMiddleware, MetricsMiddleware with DI
```

## Middleware with injected dependencies

Middleware can declare dependencies using `Inject[]`. The dependencies are automatically resolved via the container:

```{literalinclude} ../../../examples/middleware/dependencies/middleware.py
:start-after: Middleware can have container dependencies
:end-at: logger: Inject[Logger]
:emphasize-lines: 10
```

The `logger` field is injected automatically when the middleware is resolved from the container.
`self.logger` can then be used in the `__call__` method:

```{literalinclude} ../../../examples/middleware/dependencies/middleware.py
:start-at: class LoggingMiddleware:
:end-at: return props
:lines: 11-16
:emphasize-lines: 5
```

## Service definitions

Services are also marked with `@injectable` for automatic discovery. Here is the declaration of the `Logger` service
used above:

```{literalinclude} ../../../examples/middleware/dependencies/services.py
:start-after: The Logger service is
:end-at: class Logger:
```

We also have a `MetricsCollector` service that is used by the `MetricsMiddleware`:

```{literalinclude} ../../../examples/middleware/dependencies/services.py
:start-after: The MetricsCollector service is
:end-at: class MetricsCollector:
```

## Scanning discovers everything

The `scan()` function discovers services, middleware, and their dependencies:

```{literalinclude} ../../../examples/middleware/dependencies/app.py
:start-at: registry = HopscotchRegistry
:end-at: scan(registry, services, middleware)
```

## Verifying middleware behavior

Putting the logger in the container means we can grab it from anywhere, including middleware, and write to it. No magic.
Even better, it is automatically cleaned up after each "request".
Get services from the container to verify they were used:

```{literalinclude} ../../../examples/middleware/dependencies/app.py
:start-at: logger = container.get(Logger)
:end-at: assert metrics.get_count
:emphasize-lines: 5-6
```

## Running the example

```bash
uv run python -m examples.middleware.dependencies.app
```

Output:

```
<div>Simple Component</div>
```

The example uses assertions to verify behavior. All middleware logic is tested silently.

## Full source code

### `app.py`

```{literalinclude} ../../../examples/middleware/dependencies/app.py
```

### `middleware.py`

```{literalinclude} ../../../examples/middleware/dependencies/middleware.py
```

### `services.py`

```{literalinclude} ../../../examples/middleware/dependencies/services.py
```
