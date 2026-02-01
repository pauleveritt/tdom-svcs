# Middleware Scoping

This example demonstrates the two middleware mechanisms: global middleware that applies to all components, and
per-component middleware that components can opt into.

```{note}
This example uses Hopscotch patterns (`@middleware`, `@component`, `scan()`) for convenience.
You can also use imperative registration with `register_middleware()` if preferred.
```

## Project structure

```
scoping/
├── app.py              # Main entry point
├── components.py       # Button (with per-component MW), Card
└── middleware.py       # Global and async middleware
```

## Global middleware (declared)

Middleware marked with `@middleware` runs for **all components**—there is no way to exclude specific components:

```{literalinclude} ../../../examples/middleware/scoping/middleware.py
:start-at: The global logging middleware
:end-at: return props
:emphasize-lines: 18
```

## Per-component middleware (opt-in)

Components can opt into **additional** middleware using `@component`. This middleware does **not** need the
`@middleware` decorator, but must be `@injectable` for container resolution:

```{literalinclude} ../../../examples/middleware/scoping/components.py
:start-at: @injectable
:end-at: return props
```

Note that `ButtonSpecificMiddleware` has `@injectable` but no `@middleware` decorator. The **type** (not an instance)
is passed to `@component`, and the container resolves it at execution time:

```{literalinclude} ../../../examples/middleware/scoping/components.py
:start-after: Button component with per-component middleware
:end-at: class Button:
```

The `pre_resolution` key specifies when the middleware runs during component processing. Other lifecycle phases include `post_resolution` and `rendering`. See {ref}`middleware:lifecycle-phases` for details.

## Execution order

Per-component middleware is **additive**—it runs in addition to global middleware, not instead of it:

1. **Global middleware** runs first via `execute_middleware()`
2. **Per-component middleware** runs after via `execute_component_middleware()`, which resolves types from container

```{literalinclude} ../../../examples/middleware/scoping/app.py
:start-at: result = execute_middleware(Button
:end-at: execute_component_middleware(Button
```

## Async middleware

Middleware can be async by defining an async `__call__` method:

```{literalinclude} ../../../examples/middleware/scoping/middleware.py
:start-at: class AsyncDatabaseMiddleware:
:end-at: return props
:emphasize-lines: 10-14
```

Async middleware don't use `@middleware` decorator—they're registered manually when needed:

```{literalinclude} ../../../examples/middleware/scoping/app.py
:start-at: register_middleware(registry, AsyncDatabaseMiddleware)
:end-at: register_middleware(registry, SyncTransformMiddleware)
```

## Mixed sync and async chains

Use `execute_middleware_async()` when any middleware might be async:

```{literalinclude} ../../../examples/middleware/scoping/app.py
:start-at: async_result = await execute_middleware_async
:end-at: async_result = await execute_middleware_async
:emphasize-lines: 1
```

Sync middleware in an async chain are called normally; async middleware are awaited.

## Scanning discovers both decorators

The `scan()` function finds both `@middleware` and `@component` decorated classes:

```{literalinclude} ../../../examples/middleware/scoping/app.py
:start-at: scan(registry, middleware
:end-at: scan(registry, middleware
:emphasize-lines: 1
```

## Running the example

```bash
uv run python -m examples.middleware.scoping.app
```

Output:

```
<div>Simple Component</div>
```

## Full source code

### `app.py`

```{literalinclude} ../../../examples/middleware/scoping/app.py
```

### `middleware.py`

```{literalinclude} ../../../examples/middleware/scoping/middleware.py
```

### `components.py`

```{literalinclude} ../../../examples/middleware/scoping/components.py
```
