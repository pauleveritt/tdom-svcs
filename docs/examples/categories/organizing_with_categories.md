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

```{example-snippet} categories/categories_example.py#decorator-middleware
```

Each middleware gets:
- The automatic `"middleware"` kind
- Any user categories you specify
- For example: `("security", "auth")`

## Hookable Targets with Categories

Define hookable targets with categories:

```{example-snippet} categories/categories_example.py#decorator-hookables
```

Hookable targets get:
- The automatic `"hookable"` kind
- Any user categories you specify
- For example: `("page", "admin")`

## Listing Categories

List the registered kind and user categories:

```{example-snippet} categories/categories_example.py#category-listing
```

### Get Items in a Category

Retrieve all middleware or components tagged with a specific user category:

```{example-snippet} categories/categories_example.py#category-facet-query
```

### Get Categories for an Item

Find out which categories are assigned to a specific item:

```{example-snippet} categories/categories_example.py#item-category-query
```

## Dynamic Execution by Category

You can execute only middleware from specific categories:

```{example-snippet} categories/categories_example.py#middleware-execution
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
2. Show items in selected categories (security, page)
3. Display categories for specific items
4. Execute filtered middleware

## Key Takeaways

- Categories help organize middleware and components by concern
- Use decorators to declare categories: `@middleware(categories=[...])`
- Query by category: `registry.get_by_category("security")`
- Query role groups by kind: `registry.get_by_kind("middleware")`
- Items can have multiple categories for flexible organization
- Categories enable dynamic execution patterns

## Full Source Code

```{example-source} categories/categories_example
```
