# Shape: Injectable Categories Refactor

## Before (Current State)

```python
# middleware.py
MIDDLEWARE_METADATA_ATTR = "_tdom_middleware_"
MIDDLEWARE_REGISTRY_KEY = "tdom.middleware_types"

def middleware(cls):
    """Mark a class as global middleware."""
    setattr(cls, MIDDLEWARE_METADATA_ATTR, True)
    return injectable(cls)

def register_middleware(registry, middleware_type):
    """Imperative API to register middleware."""
    types = registry.get_registered_value(MIDDLEWARE_REGISTRY_KEY, set())
    types.add(middleware_type)
    registry.register_value(MIDDLEWARE_REGISTRY_KEY, types)

def get_middleware_types(registry):
    """Get all middleware types from registry."""
    return registry.get_registered_value(MIDDLEWARE_REGISTRY_KEY, set())

# scanning.py (170+ lines)
def _resolve_module(module_or_name):
    """Resolve module from string or module object."""
    # 15 lines of import logic

def _get_all_modules(package):
    """Walk package tree and collect all modules."""
    # 30 lines of module walking

def _scan_for_middleware(registry, modules):
    """Find @middleware classes and register them."""
    # 25 lines scanning for MIDDLEWARE_METADATA_ATTR

def _scan_for_component_middleware(registry, modules):
    """Find @component classes and register middleware maps."""
    # 40 lines scanning for COMPONENT_MIDDLEWARE_ATTR

def scan(registry, *packages, locals_dict=None):
    """Scan packages for injectables, middleware, and components."""
    if locals_dict:
        _scan_locals_dict(registry, locals_dict)
    else:
        svcs_scan(registry, *packages)

        # Duplicate module walking for middleware/components
        modules = []
        for pkg in packages:
            modules.extend(_get_all_modules(pkg))

        _scan_for_middleware(registry, modules)
        _scan_for_component_middleware(registry, modules)

    return registry
```

## After (Target State)

```python
# middleware.py
class middleware(injectable):
    """Mark a class as global middleware."""
    categories = ("middleware",)

def register_middleware(registry, middleware_type):
    """Imperative API to register middleware."""
    registry._register_categories(middleware_type, ["middleware"])

def get_middleware_types(registry):
    """Get all middleware types from registry."""
    return registry.get_by_category("middleware")

# services/middleware/decorators.py
class component(injectable):
    """Mark a tdom component with optional middleware config."""
    categories = ("component",)
    _middleware_config: MiddlewareMap | None = None

    def __new__(cls, target=None, *, middleware=None, **kwargs):
        result = super().__new__(cls, target, **kwargs)
        if isinstance(result, cls):
            result._middleware_config = middleware
        return result

    def __init__(self, target=None, *, middleware=None, **kwargs):
        pass

    def post_decorate(self, target, metadata):
        """Store middleware config after decoration."""
        setattr(target, COMPONENT_MIDDLEWARE_ATTR, self._middleware_config or {})

# scanning.py (30 lines)
def _register_component_middlewares(registry):
    """Register MiddlewareMap configs for @component-decorated types."""
    for comp_type in registry.get_by_category("component"):
        mw_config = getattr(comp_type, COMPONENT_MIDDLEWARE_ATTR, {})
        if mw_config:
            register_component_middleware(registry, comp_type, mw_config)

def scan(registry, *packages, locals_dict=None):
    """Scan packages for all injectables (services, middleware, components)."""
    if locals_dict is not None:
        svcs_scan(registry, locals_dict=locals_dict)
    else:
        svcs_scan(registry, *packages)

    # Component middleware maps need post-scan registration
    _register_component_middlewares(registry)
    return registry
```

## Key Changes

1. **No more custom metadata attributes** — `MIDDLEWARE_METADATA_ATTR` removed entirely
2. **No more registry keys** — `MIDDLEWARE_REGISTRY_KEY` removed, categories replace it
3. **Single-pass scanning** — svcs_scan() discovers everything, no duplicate module walking
4. **140 lines of code deleted** — all duplicate module-walking logic eliminated
5. **Decorators become classes** — but preserve the same API surface
6. **Post-scan step simplified** — only needed for component middleware config registration

## Public API Preserved

All existing user code continues to work:

```python
# Bare decorator usage — unchanged
@middleware
class MyMiddleware:
    pass

@component
class MyComponent:
    pass

# Parameterized usage — unchanged
@component(middleware={"before": [SomeMiddleware]})
class MyComponent:
    pass

# Imperative registration — unchanged
register_middleware(registry, MyMiddleware)

# Introspection — unchanged
middlewares = list_middlewares(registry)
components = list_components(registry)
```
