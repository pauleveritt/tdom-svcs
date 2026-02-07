# Imperative Categories

This example demonstrates using imperative registration functions (`register_middleware` and `register_component`) with additional categories.

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

```{literalinclude} ../../../examples/categories/imperative_categories.py
:start-after: # Define middleware classes
:end-before: # Define component classes
```

Then register them:

```{literalinclude} ../../../examples/categories/imperative_categories.py
:start-after: # Register middleware with categories
:end-before: # Register components
```

## Imperative Component Registration

Register components with categories using `register_component()`:

```{literalinclude} ../../../examples/categories/imperative_categories.py
:start-after: # Define component classes
:end-before: def main()
```

Then register them:

```{literalinclude} ../../../examples/categories/imperative_categories.py
:start-after: # Register components with categories
:end-before: # Query and display
```

## Querying Results

After registration, query the registry:

```{literalinclude} ../../../examples/categories/imperative_categories.py
:start-after: # Query and display results
:end-before: return results
```

## Running the Example

```bash
uv run python examples/categories/imperative_categories.py
```

The example will show:
1. All categories registered
2. Items in each category (security, compliance, page, protected)
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
- Use `register_component()` with `categories=` parameter
- Imperative registration is useful for third-party classes
- Mix decorator and imperative approaches as needed
- Categories work the same way regardless of registration method

## Full Source Code

```{literalinclude} ../../../examples/categories/imperative_categories.py
```
