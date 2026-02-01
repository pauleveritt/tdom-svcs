# Path Middleware - References

## tdom-path Implementation

### Key Files

**`/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/tree.py`**
- `AssetReference` dataclass - stores source Traversable and module_path
- `_should_process_href()` - filters external/special URLs
- `_EXTERNAL_URL_PATTERN` - regex for URL detection
- `_walk_tree()` - recursive Node tree traversal
- `make_path_nodes()` - transforms asset paths to Traversable

**`/Users/pauleveritt/projects/t-strings/tdom-path/src/tdom_path/webpath.py`**
- `make_traversable()` - creates Traversable from component + relative path
- `_normalize_module_name()` - handles `__main__` and similar

### Patterns to Reuse

1. **URL Filtering Pattern**
   ```python
   _EXTERNAL_URL_PATTERN = re.compile(
       r"^(https?://|//|mailto:|tel:|data:|javascript:|#)", re.IGNORECASE
   )
   ```

2. **Tree Walking Pattern**
   ```python
   def _walk_tree(node: Node, transform_fn: Callable[[Node], Node]) -> Node:
       # Apply transformation
       transformed = transform_fn(node)
       # Recurse into children if present
       match transformed:
           case Element(children=children) if children:
               # Walk children
           case Fragment(children=children) if children:
               # Walk children
           case _:
               return transformed
   ```

3. **Asset Detection Pattern**
   ```python
   match node:
       case Element(tag="link"):
           # Check href attribute
       case Element(tag="script"):
           # Check src attribute
   ```

## Existing Middleware Examples

### `examples/middleware/basic/`
- `app.py` - Shows registry setup, container usage, middleware registration
- `middleware.py` - Shows middleware dataclass pattern with priority

### Key Patterns

1. **Registry Setup**
   ```python
   registry = HopscotchRegistry()
   scan(registry, services, components)
   setup_container(context, registry)
   ```

2. **Middleware Registration**
   ```python
   manager = container.get(MiddlewareManager)
   manager.register_middleware(MyMiddleware())
   ```

3. **Middleware Structure**
   ```python
   @dataclass
   class MyMiddleware:
       priority: int = 0

       def __call__(self, component, props, context) -> dict:
           # Do something
           return props
   ```

## Middleware Manager

### `src/tdom_svcs/services/middleware/middleware_manager.py`
- `register_middleware()` - registers middleware instance
- `register_middleware_service()` - registers middleware type for DI resolution
- `execute()` - runs middleware chain
- Priority ordering (lower numbers first)

## Types

### `src/tdom_svcs/types.py`
- `Component = type | Callable[..., Any]`
- `Props = dict[str, Any]`
- `Context` Protocol - dict-like access
- `Middleware` Protocol - priority + __call__
