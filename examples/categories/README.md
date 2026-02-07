# Category Organization Examples

These examples demonstrate how to use additional categories to organize and filter middleware and components in tdom-svcs.

## What are Categories?

Categories are tags that you can attach to middleware and components. Every middleware automatically gets the `"middleware"` category, and every component gets the `"component"` category. You can add additional categories to organize and filter your items.

## Use Cases

- **Organization**: Tag middleware as "security", "logging", "analytics"
- **Filtering**: Query only middleware in a specific category
- **Dynamic Configuration**: Build menus or configurations based on categories
- **Separation of Concerns**: Group related middleware/components together

## Examples

### 1. Organizing with Categories (`organizing_with_categories.py`)

Demonstrates the decorator approach:

```python
# Middleware with multiple categories
@middleware(categories=["security", "auth"])
@dataclass
class AuthenticationMiddleware:
    priority: int = -20
    def __call__(self, component, props, context):
        return props

# Component with multiple categories
@component(categories=["page", "admin"])
@dataclass
class AdminDashboard:
    title: str = "Admin Dashboard"

# Query by category
security_middleware = registry.get_by_category("security")
admin_pages = registry.get_by_category("admin")
```

**Run it:**
```bash
uv run python examples/categories/organizing_with_categories.py
```

### 2. Imperative Categories (`imperative_categories.py`)

Shows how to use categories with imperative registration:

```python
# Register with categories
register_middleware(
    registry,
    SecurityMiddleware,
    categories=["security", "compliance"]
)

register_component(
    registry,
    SecurePage,
    categories=["page", "protected"]
)

# Query
compliance_items = registry.get_by_category("compliance")
```

**Run it:**
```bash
uv run python examples/categories/imperative_categories.py
```

## API Reference

### Decorator Forms

**Middleware:**
```python
@middleware(categories=["cat1", "cat2"])
class MyMiddleware:
    pass
# Has categories: ("middleware", "cat1", "cat2")
```

**Component:**
```python
@component(categories=["cat1", "cat2"])
class MyComponent:
    pass
# Has categories: ("component", "cat1", "cat2")

@component(middleware={...}, categories=["cat1"])
class MyComponent:
    pass
# Both middleware config and categories
```

### Imperative Forms

**Middleware:**
```python
register_middleware(
    registry,
    MyMiddleware,
    categories=["cat1", "cat2"]
)
```

**Component:**
```python
register_component(
    registry,
    MyComponent,
    middleware={...},  # optional
    categories=["cat1", "cat2"]
)
```

### Querying Categories

```python
# List all categories
all_categories = registry.list_categories()

# Get items in a category
items = registry.get_by_category("security")

# Get categories for an item
categories = registry.get_categories(MyMiddleware)

# Check if item has a category
has_it = registry.has_category(MyMiddleware, "security")
```

## Best Practices

1. **Use descriptive category names**: "security", "logging", "analytics" (not "misc", "utils")
2. **Be consistent**: Use the same category names across your codebase
3. **Don't over-categorize**: 2-3 additional categories per item is usually enough
4. **Document your categories**: Explain what each category means in your project
5. **Consider hierarchy**: Use categories like "security.auth", "security.validation" for subcategories

## Common Categories

**Middleware:**
- `security`, `auth`, `validation`
- `logging`, `analytics`, `monitoring`
- `caching`, `performance`
- `error-handling`, `retry`

**Components:**
- `page`, `widget`, `layout`
- `admin`, `public`, `protected`
- `interactive`, `display`, `form`
- `dashboard`, `settings`, `profile`
