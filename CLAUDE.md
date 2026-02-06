# Claude Code Instructions

## Python Tooling

Always use the Astral tools for Python development:

- **uv** - Python package and project manager (use `astral:uv` skill)
- **ruff** - Fast Python linter and formatter (use `astral:ruff` skill)
- **ty** - Fast Python type checker and LSP (use `astral:ty` skill)

## Type Checking

Use `ty` as the Python language server and type checker:

```bash
# Check types
uv run ty check src/

# Use ty LSP for IDE integration
```

## Project Overview

tdom-svcs integrates svcs dependency injection with tdom:

- `Component` type alias for tdom components
- `@component` decorator with middleware support
- `html()` function with DI context
- Component middleware system
