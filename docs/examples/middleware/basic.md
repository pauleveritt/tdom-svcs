# Basic Middleware

This example demonstrates the fundamental middleware patterns: chain execution, priority ordering, and halting.

## Project structure

```
basic/
├── app.py              # Main entry point
├── components.py       # Greeting component
├── services.py         # Database, Users services
├── middleware.py       # Logging, Validation, Transformation middleware
├── request.py          # Request dataclass
└── site/
    └── __init__.py     # Site configuration placeholder
```

## What is middleware?

Middleware are callables that intercept component processing. Each middleware receives:
- `component`: The component class being processed
- `props`: A dictionary of properties
- `context`: The current context (container or dict)

Middleware returns either modified `props` (to continue) or `None` (to halt).

## Defining middleware

Middleware are simple dataclasses with a `priority` attribute and a `__call__` method:

```{literalinclude} ../../../examples/middleware/basic/middleware.py
:start-at: @dataclass
:end-before: @dataclass
:lines: 1-14
```

## Priority ordering

Middleware execute in priority order—lower numbers run first:

```{literalinclude} ../../../examples/middleware/basic/middleware.py
:start-at: class LoggingMiddleware
:end-at: priority: int = -10
```

```{literalinclude} ../../../examples/middleware/basic/middleware.py
:start-at: class ValidationMiddleware
:end-at: priority: int = 0
```

```{literalinclude} ../../../examples/middleware/basic/middleware.py
:start-at: class TransformationMiddleware
:end-at: priority: int = 10
```

This ensures logging (-10) happens before validation (0), which happens before transformation (10).

## Halting execution

Middleware can halt the chain by returning `None`:

```{literalinclude} ../../../examples/middleware/basic/middleware.py
:start-at: class ValidationMiddleware
:end-at: return props
```

When ValidationMiddleware finds missing required props, it returns `None` and no subsequent middleware runs.

## Running the example

```bash
uv run python -m examples.middleware.basic.app
```

Output:
```
==================================================
Test 1: Valid props (should pass all middleware)
==================================================
[LOG] Processing Button with props: ['title', 'variant']
[VALIDATION] Props validated successfully
[TRANSFORM] Added 'transformed' flag to props

Result: {'title': 'Click Me', 'variant': 'primary', 'transformed': True}

==================================================
Test 2: Invalid props (should halt at validation)
==================================================
[LOG] Processing Button with props: ['variant']
[VALIDATION] Error: 'title' field is required

Result: None (execution halted)
```

## Full source code

### app.py

```{literalinclude} ../../../examples/middleware/basic/app.py
```

### middleware.py

```{literalinclude} ../../../examples/middleware/basic/middleware.py
```

### components.py

```{literalinclude} ../../../examples/middleware/basic/components.py
```

### services.py

```{literalinclude} ../../../examples/middleware/basic/services.py
```
