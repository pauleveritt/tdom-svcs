# Middleware with Dependencies

This example demonstrates middleware that depend on services like Logger and MetricsCollector, using dependency injection and factory functions.

## Project structure

```
dependencies/
├── app.py              # Main entry point
├── components.py       # Greeting component
├── services.py         # Database, Users, Logger, MetricsCollector
├── middleware.py       # LoggingMiddleware, MetricsMiddleware with DI
├── request.py          # Request dataclass
└── site/
    ├── __init__.py     # Site configuration with FakeLogger
    └── services.py     # FakeLogger for testing
```

## Middleware with service dependencies

Middleware often need access to services like loggers or metrics collectors. Rather than creating these internally, we inject them:

```{literalinclude} ../../../examples/middleware/dependencies/middleware.py
:start-at: class LoggingMiddleware
:end-at: return props
```

The `logger` field is injected when the middleware is constructed via a factory function.

## Service definitions

The Logger and MetricsCollector are simple dataclasses:

```{literalinclude} ../../../examples/middleware/dependencies/services.py
:start-at: class Logger
:end-at: return self.messages.copy()
```

```{literalinclude} ../../../examples/middleware/dependencies/services.py
:start-at: class MetricsCollector
:end-at: return self._metrics.copy()
```

## Factory functions for DI

To inject services into middleware, use factory functions:

```{literalinclude} ../../../examples/middleware/dependencies/app.py
:start-at: def create_logging_middleware
:end-at: registry.register_factory(MetricsMiddleware
```

Then register the middleware with the manager using `register_middleware_service`:

```{literalinclude} ../../../examples/middleware/dependencies/app.py
:start-at: manager.register_middleware_service(LoggingMiddleware
:end-at: manager.register_middleware_service(MetricsMiddleware
```

## Testing with fakes

The site demonstrates how to replace services with fakes for testing:

```{literalinclude} ../../../examples/middleware/dependencies/site/services.py
:start-at: @dataclass
:end-at: self.messages.clear()
```

The site's `svcs_registry()` is called automatically during `scan()` and registers the FakeLogger:

```{literalinclude} ../../../examples/middleware/dependencies/site/__init__.py
```

## Running the example

```bash
uv run python -m examples.middleware.dependencies.app
```

Output:
```
==================================================
Processing multiple components
==================================================

Logger type: FakeLogger
Logger messages (3):
  [TEST] INFO: Processing Button
  [TEST] INFO: Processing Button
  [TEST] INFO: Processing Button

Metrics:
  Button count: 3
```

## Full source code

### app.py

```{literalinclude} ../../../examples/middleware/dependencies/app.py
```

### middleware.py

```{literalinclude} ../../../examples/middleware/dependencies/middleware.py
```

### services.py

```{literalinclude} ../../../examples/middleware/dependencies/services.py
```

### site/\_\_init\_\_.py

```{literalinclude} ../../../examples/middleware/dependencies/site/__init__.py
```

### site/services.py

```{literalinclude} ../../../examples/middleware/dependencies/site/services.py
```
