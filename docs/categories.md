# Additional Categories

Both `@middleware` and `@hookable` decorators (and their imperative counterparts) support additional categories for organizing and filtering your middleware and hookable targets.

## Overview

Every middleware automatically gets the `"middleware"` category, and every hookable target gets the `"hookable"` category. You can add additional categories to tag items for:

- **Organization**: Group related items together
- **Filtering**: Query subsets of middleware/hookables
- **Dynamic Configuration**: Build menus or features based on categories
- **Separation of Concerns**: Tag items by purpose (security, logging, etc.)

## Decorator Forms

### Middleware

```python
from tdom_svcs import middleware

# Basic usage - only "middleware" category
@middleware
@dataclass
class LoggingMiddleware:
    priority: int = 0
    def __call__(self, target, props, context):
        return props

# With additional categories
@middleware(categories=["security", "auth"])
@dataclass
class AuthMiddleware:
    priority: int = -10
    def __call__(self, target, props, context):
        # Categories: ("middleware", "security", "auth")
        return props
```

### Hookable

```python
from tdom_svcs import hookable

# Basic usage - only "hookable" category
@hookable
@dataclass
class Button:
    label: str = "Click"

# With additional categories
@hookable(categories=["page", "admin"])
@dataclass
class AdminDashboard:
    # Categories: ("hookable", "page", "admin")
    title: str = "Admin"

# With both middleware config and categories
@hookable(
    middleware={"pre_resolution": [AuthMiddleware]},
    categories=["page", "protected"]
)
@dataclass
class SecurePage:
    # Has middleware config AND categories
    title: str = "Secure Area"
```

## Imperative Forms

### Register Middleware

```python
from tdom_svcs import register_middleware

# Basic registration - only "middleware" category
register_middleware(registry, LoggingMiddleware)

# With additional categories
register_middleware(
    registry,
    AuthMiddleware,
    categories=["security", "compliance"]
)
# Categories: ("middleware", "security", "compliance")
```

### Register Hookable

```python
from tdom_svcs import register_hookable

# Basic registration - only "hookable" category
register_hookable(registry, Button)

# With additional categories
register_hookable(
    registry,
    AdminPage,
    categories=["page", "admin"]
)

# With middleware config and categories
register_hookable(
    registry,
    SecurePage,
    middleware={"pre_resolution": [AuthMiddleware]},
    categories=["page", "protected"]
)
```

## Querying by Category

Once items are registered with categories, you can query them:

```python
# List all category names in the registry
all_categories = registry.list_categories()
# Returns: ["middleware", "hookable", "security", "page", ...]

# Get all items in a specific category
security_items = list(registry.get_by_category("security"))
# Returns: [AuthMiddleware, ValidationMiddleware, ...]

admin_pages = list(registry.get_by_category("admin"))
# Returns: [AdminDashboard, AdminSettings, ...]

# Get all categories for a specific item
categories = registry.get_categories(AuthMiddleware)
# Returns: frozenset(["middleware", "security", "auth"])

# Check if an item has a specific category
is_secure = registry.has_category(AuthMiddleware, "security")
# Returns: True
```

## Use Cases

### 1. Filtering Middleware by Purpose

Execute only security-related middleware:

```python
from tdom_svcs import execute_middleware

# Get security middleware
security_middleware = list(registry.get_by_category("security"))

with HopscotchContainer(registry) as container:
    props = {"user": "alice"}

    # Execute only security middleware
    for mw_type in sorted(security_middleware, key=lambda m: m().priority):
        mw = container.get(mw_type)
        props = mw(MyComponent, props, container)
```

### 2. Building Dynamic Menus

Build a navigation menu from page components:

```python
# Get all page components
pages = registry.get_by_category("page")

# Build menu
menu_items = []
for page_cls in pages:
    # Check if it's an admin page
    is_admin = registry.has_category(page_cls, "admin")
    is_public = registry.has_category(page_cls, "public")

    menu_items.append({
        "name": page_cls.__name__,
        "access": "admin" if is_admin else "public"
    })
```

### 3. Conditional Feature Loading

Load features based on categories:

```python
# Load analytics middleware only in production
if is_production:
    analytics_items = registry.get_by_category("analytics")
    # Register or configure analytics middleware

# Load development-only middleware
if is_development:
    debug_items = registry.get_by_category("debug")
    # Register debug middleware
```

### 4. Compliance Auditing

Find all items tagged with compliance categories:

```python
# Audit report
compliance_middleware = registry.get_by_category("compliance")
security_items = registry.get_by_category("security")

print("Compliance Audit:")
print(f"  Compliance middleware: {len(compliance_middleware)}")
print(f"  Security middleware: {len(security_items)}")
```

## Best Practices

1. **Use descriptive names**: Choose clear category names like "security", "logging", "analytics"
2. **Be consistent**: Use the same category names throughout your codebase
3. **Don't over-categorize**: 2-3 additional categories per item is usually sufficient
4. **Document your categories**: Explain what each category means in your project documentation
5. **Consider namespacing**: Use prefixes like "security.auth", "security.validation" for related categories

## Common Category Patterns

**Middleware Categories:**
- `security`, `auth`, `authorization`, `validation`
- `logging`, `analytics`, `monitoring`, `metrics`
- `caching`, `performance`, `optimization`
- `error-handling`, `retry`, `timeout`
- `debug`, `development`, `testing`

**Hookable Target Categories:**
- `page`, `widget`, `layout`, `container`
- `admin`, `public`, `protected`, `restricted`
- `interactive`, `display`, `form`, `input`
- `dashboard`, `settings`, `profile`, `menu`

## Examples

See `examples/categories/` for complete working examples demonstrating both decorator and imperative approaches.

## See Also

- {doc}`services/middleware` - Middleware system documentation
- {doc}`core_concepts` - Core concepts and patterns
- {doc}`examples/categories/index` - Category examples
- [svcs-di Categories](https://github.com/hynek/svcs-di) - Upstream category system
