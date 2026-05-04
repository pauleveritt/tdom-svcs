# Organizing with Categories (Decorator Approach)

This example demonstrates using the `@middleware` and `@hookable` decorators with additional categories to organize and query your application structure.

## Overview

The decorator approach lets you declare categories directly on your classes:

```python
@middleware(categories=["security", "auth"])
@dataclass
class AuthenticationMiddleware:
    priority: int = -20

    def __call__(self, target, props, context):
        props["authenticated"] = True
        return props
```

## Middleware with Categories

Define middleware with multiple categories:

```{literalinclude} ../../../examples/categories/categories_example.py
:lines: 21-42
```

Each middleware gets:
- The automatic `"middleware"` category
- Any additional categories you specify
- For example: `("middleware", "security", "auth")`

## Hookable Targets with Categories

Define hookable targets with categories:

```{literalinclude} ../../../examples/categories/categories_example.py
:lines: 45-58
```

Hookable targets get:
- The automatic `"hookable"` category
- Any additional categories you specify
- For example: `("hookable", "page", "admin")`

## Querying by Category

The registry provides methods to query items by category:

```{literalinclude} ../../../examples/categories/categories_example.py
:lines: 101-117
```

### Get Items in a Category

Retrieve all middleware or components tagged with a specific category:

```{literalinclude} ../../../examples/categories/categories_example.py
:lines: 105-117
```

### Get Categories for an Item

Find out which categories are assigned to a specific item:

```{literalinclude} ../../../examples/categories/categories_example.py
:lines: 119-121
```

## Dynamic Execution by Category

You can execute only middleware from specific categories:

```{literalinclude} ../../../examples/categories/categories_example.py
:lines: 123-138
```

This allows you to:
- Filter middleware by concern (security, logging, etc.)
- Execute subsets of middleware for specific scenarios
- Build dynamic pipelines based on configuration

## Running the Example

```bash
uv run python examples/categories/categories_example.py
```

The example will:
1. List all categories in the registry
2. Show items in specific categories (security, interactive)
3. Display categories for specific items
4. Execute filtered middleware

## Key Takeaways

- Categories help organize middleware and components by concern
- Use decorators to declare categories: `@middleware(categories=[...])`
- Query by category: `registry.get_by_category("security")`
- Items can have multiple categories for flexible organization
- Categories enable dynamic execution patterns

## Full Source Code

```{literalinclude} ../../../examples/categories/categories_example.py
```
