# Basic Middleware

This example demonstrates the fundamental middleware patterns: chain execution, priority ordering, halting, and prop transformation.

```{note}
This example uses Hopscotch patterns (`@middleware`, `scan()`) for convenience.
You can also use imperative registration with `register_middleware()` if preferred.
```

## Project structure

```
basic/
├── app.py              # Main entry point
└── middleware.py       # Logging, Validation, Transformation middleware
```

## What is middleware?

Middleware are callables that intercept component processing. Each middleware receives:
- `component`: The component class being processed
- `props`: A dictionary of properties
- `context`: The current context (container)

Middleware returns either modified `props` (to continue) or `None` (to halt).

## Defining middleware with decorators

Middleware classes are marked with the `@middleware` decorator:

```{literalinclude} ../../../examples/middleware/basic/middleware.py
:start-at: Define middleware with
:end-at: class LoggingMiddleware:
```

The `@middleware` decorator both marks the class for discovery by `scan()` and makes it injectable for DI resolution.

## Priority ordering

Middleware execute in priority order—lower numbers run first:

```{literalinclude} ../../../examples/middleware/basic/middleware.py
:start-after: Define middleware with
:end-at: priority: int = -10
```

Recommended priority ranges:
- `-10`: Logging, metrics (observe but don't modify)
- `0`: Validation (check props are valid)
- `10`: Transformation (modify props)

## Halting execution

Middleware can halt the chain by returning `None`:

```{literalinclude} ../../../examples/middleware/basic/middleware.py
:start-at: class ValidationMiddleware:
:end-at: return props
:emphasize-lines: 13-14
```

When ValidationMiddleware finds missing required props, it returns `None` and no subsequent middleware runs.

## Prop transformation

Middleware can modify props and pass them to the next middleware:

```{literalinclude} ../../../examples/middleware/basic/middleware.py
:start-at: class TransformationMiddleware:
:end-at: return props
:emphasize-lines: 11
```

## Scanning and setup

The `scan()` function discovers both `@injectable` services and `@middleware` classes:

```{literalinclude} ../../../examples/middleware/basic/app.py
:start-at: registry = HopscotchRegistry
:end-at: scan(registry, middleware)
```

## Running the example

```bash
uv run python -m examples.middleware.basic.app
```

Output:
```
<div>Simple Component</div>
```

The example uses assertions to verify behavior. All middleware logic is tested silently.

## Full source code

### `app.py`

```{literalinclude} ../../../examples/middleware/basic/app.py
```

### `middleware.py`

```{literalinclude} ../../../examples/middleware/basic/middleware.py
```
