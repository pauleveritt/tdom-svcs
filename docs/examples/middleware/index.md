# Middleware Examples

tdom-svcs middleware enables operating on rendered component output for
tdom-specific use cases like accessibility checking.

## Overview

For general middleware concepts (chain execution, priority ordering, dependencies, etc.), see the [svcs-di middleware documentation](https://github.com/hynek/svcs-di).

These examples demonstrate **tdom-specific** middleware patterns:

| Example | Description |
|---------|-------------|
| [Aria](aria) | Accessibility validation by inspecting rendered HTML |

## Key tdom Patterns

**Rendered Output Inspection:** Middleware can render targets and inspect the
resulting output.

**Container Context:** Middleware receives the DI container, enabling access to services like loggers, configuration, and application state.

**Per-Target Middleware:** Use `@hookable` to attach middleware to specific targets, executing only when those targets are processed.

## Running Examples

All examples can be run directly:

```bash
uv run python -m examples.middleware.aria.app
```

```{toctree}
:hidden:
:maxdepth: 1

aria
```
