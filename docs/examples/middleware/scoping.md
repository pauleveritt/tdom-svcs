# Middleware Scoping

This example demonstrates different middleware scopes: global middleware that applies to all components, per-component middleware via decorators, and async middleware support.

## Project structure

```
scoping/
├── app.py              # Main entry point
├── components.py       # Greeting, Button (with per-component MW), Card
├── services.py         # Database, Users services
├── middleware.py       # Global and async middleware
├── request.py          # Request dataclass
└── site/
    └── __init__.py     # Site configuration placeholder
```

## Global middleware

Global middleware registered with MiddlewareManager applies to all components:

```{literalinclude} ../../../examples/middleware/scoping/middleware.py
:start-at: class GlobalLoggingMiddleware
:end-at: return props
```

Register global middleware with the manager:

```{literalinclude} ../../../examples/middleware/scoping/app.py
:start-at: global_logging = GlobalLoggingMiddleware
:end-at: manager.register_middleware(GlobalValidationMiddleware())
```

## Per-component middleware

For middleware that should only apply to specific components, use the `@component` decorator:

```{literalinclude} ../../../examples/middleware/scoping/components.py
:start-at: class ButtonSpecificMiddleware
:end-at: return props
```

Apply it to a component:

```{literalinclude} ../../../examples/middleware/scoping/components.py
:start-at: button_mw = ButtonSpecificMiddleware
:end-at: variant: str = "default"
```

Retrieve and execute per-component middleware manually:

```{literalinclude} ../../../examples/middleware/scoping/app.py
:start-at: component_mw = get_component_middleware
:end-at: result = mw_result
```

## Execution order

1. **Global middleware** runs first, in priority order
2. **Per-component middleware** runs after global middleware completes

## Async middleware

Middleware can be async by defining an async `__call__` method:

```{literalinclude} ../../../examples/middleware/scoping/middleware.py
:start-at: class AsyncDatabaseMiddleware
:end-at: return props
```

## Mixed sync and async chains

The middleware system automatically handles mixed chains. Use `execute_async()` when any middleware might be async:

```{literalinclude} ../../../examples/middleware/scoping/app.py
:start-at: async_manager = MiddlewareManager
:end-at: async_result = await async_manager.execute_async
```

Sync middleware in an async chain are called normally; async middleware are awaited.

## Running the example

```bash
uv run python -m examples.middleware.scoping.app
```

Output:
```
==================================================
Test 1: Button with per-component middleware
==================================================
[GLOBAL LOG] Processing Button
[GLOBAL VALIDATION] Props valid
After global middleware: {'title': 'Click Me'}
[BUTTON MW] Added default variant=primary
After per-component middleware: {'title': 'Click Me', 'variant': 'primary'}

==================================================
Test 2: Card without per-component middleware
==================================================
[GLOBAL LOG] Processing Card
[GLOBAL VALIDATION] Props valid
Card result: {'title': 'Welcome', 'content': 'Hello there!'}
Card per-component middleware: {}

==================================================
Test 3: Async middleware chain
==================================================
[GLOBAL LOG] Processing Dashboard
[ASYNC DB] Fetched user data for Dashboard
[ASYNC VALIDATION] Props valid
[SYNC TRANSFORM] Added _sync_processed flag
Async result: {'title': 'Main Dashboard', '_db_user': {'id': 123, 'name': 'John Doe'}, '_sync_processed': True}
```

## Full source code

### app.py

```{literalinclude} ../../../examples/middleware/scoping/app.py
```

### middleware.py

```{literalinclude} ../../../examples/middleware/scoping/middleware.py
```

### components.py

```{literalinclude} ../../../examples/middleware/scoping/components.py
```
