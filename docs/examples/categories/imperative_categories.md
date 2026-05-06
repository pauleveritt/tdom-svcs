# Imperative Categories

This example demonstrates using imperative registration functions (`register_middleware` and `register_hookable`) with additional categories.

## Overview

The imperative approach gives you control over when and how items are registered with categories:

```python
register_middleware(
    registry,
    SecurityMiddleware,
    categories=["security", "compliance"]
)
```

This is useful when:
- You don't want to use decorators
- You need to register items conditionally
- You're integrating third-party classes
- You want to vary categories based on configuration

## Imperative Middleware Registration

Register middleware with categories using `register_middleware()`:

```{example-snippet} categories/categories_example.py#imperative-middleware
```

Then register them:

```{example-snippet} categories/categories_example.py#scan-and-register
```

## Imperative Hookable Registration

Register hookable targets with categories using `register_hookable()`:

```{example-snippet} categories/categories_example.py#imperative-hookable
```

Then register them:

```{example-snippet} categories/categories_example.py#scan-and-register
```

## Querying Results

After registration, query the registry:

```{example-snippet} categories/categories_example.py#category-queries
```

## Running the Example

```bash
uv run python examples/categories/categories_example.py
```

The example will show:
1. All categories registered
2. Items in selected categories (security, page)
3. Verification that imperative registration works correctly

## When to Use Imperative Registration

**Use decorators when:**
- You control the class definitions
- You want a declarative style
- Categories are fixed at definition time

**Use imperative registration when:**
- Integrating third-party classes
- Categories depend on runtime configuration
- You need conditional registration
- You prefer explicit over implicit

## Combining Both Approaches

You can mix decorator and imperative approaches in the same application:

```python
# Decorator approach
@middleware(categories=["security"])
class AuthMiddleware:
    pass

# Imperative approach
register_middleware(
    registry,
    ThirdPartyMiddleware,
    categories=["logging"]
)

# Both work together
scan(registry, locals_dict=globals())  # Discovers decorated classes
# Imperatively registered classes are already in registry
```

## Key Takeaways

- Use `register_middleware()` with `categories=` parameter
- Use `register_hookable()` with `categories=` parameter
- Imperative registration is useful for third-party classes
- Mix decorator and imperative approaches as needed
- Categories work the same way regardless of registration method

## Full Source Code

```{example-source} categories/categories_example
```
