# Middleware Examples

Middleware allows you to intercept and modify component rendering, adding cross-cutting concerns like logging, caching, or authentication checks.

## Overview

These examples demonstrate the middleware system through progressive complexity:

| Example | Description |
|---------|-------------|
| [Basic](basic_middleware) | Chain execution, priority ordering, halting |
| [Dependencies](dependencies) | Middleware with injected services, testing with fakes |
| [Error Handling](error_handling) | Exception handling, fallback rendering, circuit breaker |
| [Scoping](scoping) | Global vs per-component middleware, async support |
| [Path](path) | Path-based middleware for asset collection |

## Key Concepts

**Chain Execution:** Middleware execute in sequence, each receiving the props from the previous middleware and passing them to the next.

**Priority Ordering:** Lower priority numbers run first (-10 before 0 before 10). Use negative numbers for early middleware (logging) and positive for late (transformation).

**Halting:** Any middleware can halt the chain by returning `None`. This is useful for validation or authorization checks.

**Service Integration:** Middleware can depend on services via factory functions and `register_middleware()`.

## Running Examples

All examples can be run directly:

```bash
# Using uv
uv run python -m examples.middleware.basic.app
uv run python -m examples.middleware.dependencies.app
uv run python -m examples.middleware.error_handling.app
uv run python -m examples.middleware.scoping.app
uv run python -m examples.middleware.path.app
```

```{toctree}
:hidden:
:maxdepth: 1

basic_middleware
dependencies
error_handling
scoping
path
```
