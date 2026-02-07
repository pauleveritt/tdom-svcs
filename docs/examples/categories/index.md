# Category Organization

Categories are tags that help organize and filter middleware and components in tdom-svcs. Every middleware automatically gets the `"middleware"` category, and every component gets the `"component"` category. You can add additional categories to organize your application.

## What are Categories?

Categories provide a way to:

- **Organize**: Tag middleware as "security", "logging", "analytics"
- **Filter**: Query only middleware or components in specific categories
- **Configure**: Build dynamic configurations based on categories
- **Separate concerns**: Group related functionality together

## Examples

```{toctree}
:maxdepth: 1

organizing_with_categories
imperative_categories
```

## Use Cases

### Middleware Organization

Group middleware by function:

```python
# Security-related middleware
@middleware(categories=["security", "auth"])
class AuthenticationMiddleware:
    pass

@middleware(categories=["security", "validation"])
class InputValidationMiddleware:
    pass

# Query all security middleware
security_middleware = registry.get_by_category("security")
```

### Component Organization

Organize components by page type or access level:

```python
@component(categories=["page", "admin"])
class AdminDashboard:
    pass

@component(categories=["widget", "interactive"])
class Button:
    pass

# Get all admin pages
admin_pages = registry.get_by_category("admin")
```

### Dynamic Configuration

Build menus or process configurations based on categories:

```python
# Execute only security middleware
security_middleware = registry.get_by_category("security")
for mw_type in sorted(security_middleware, key=lambda m: container.get(m).priority):
    mw = container.get(mw_type)
    props = mw(component, props, container)
```

## API Reference

### Querying Categories

```python
# List all categories in registry
all_categories = registry.list_categories()

# Get all items in a category
items = registry.get_by_category("security")

# Get all categories for a specific item
categories = registry.get_categories(MyMiddleware)

# Check if item has a category
has_category = registry.has_category(MyMiddleware, "security")
```

### Decorator Forms

Add categories to middleware:

```python
@middleware(categories=["cat1", "cat2"])
@dataclass
class MyMiddleware:
    priority: int = 0
    # Has categories: ("middleware", "cat1", "cat2")
```

Add categories to components:

```python
@component(categories=["cat1", "cat2"])
@dataclass
class MyComponent:
    # Has categories: ("component", "cat1", "cat2")
    pass

# Components can have both middleware config and categories
@component(
    middleware={"pre_resolution": [SomeMiddleware]},
    categories=["cat1"]
)
@dataclass
class ComponentWithMiddleware:
    pass
```

### Imperative Forms

Register middleware with categories:

```python
register_middleware(
    registry,
    MyMiddleware,
    categories=["cat1", "cat2"]
)
```

Register components with categories:

```python
register_component(
    registry,
    MyComponent,
    middleware={...},  # optional
    categories=["cat1", "cat2"]
)
```

## Best Practices

1. **Use descriptive names**: Choose clear category names like "security", "logging", "analytics" rather than generic names like "misc" or "utils"

2. **Be consistent**: Use the same category names throughout your codebase

3. **Don't over-categorize**: 2-3 additional categories per item is usually sufficient

4. **Document categories**: Create a central place documenting what each category means in your project

5. **Consider hierarchy**: Use dotted names like "security.auth" and "security.validation" for related subcategories

## Common Category Patterns

### Middleware Categories

- **Security**: `security`, `auth`, `validation`, `authorization`
- **Monitoring**: `logging`, `analytics`, `monitoring`, `metrics`
- **Performance**: `caching`, `performance`, `optimization`
- **Error handling**: `error-handling`, `retry`, `fallback`

### Component Categories

- **Structure**: `page`, `widget`, `layout`, `form`
- **Access level**: `admin`, `public`, `protected`, `authenticated`
- **Interactivity**: `interactive`, `display`, `input`
- **Purpose**: `dashboard`, `settings`, `profile`, `navigation`

## Next Steps

- Read {doc}`organizing_with_categories` for decorator-based examples
- Read {doc}`imperative_categories` for imperative registration examples
- Explore the {doc}`../middleware/index` for middleware patterns
