# References

## svcs-di Middleware

- Commit: `8e2bc03` - Added middleware system to svcs-di
- Location: `svcs_di/middleware.py`
- Key exports:
  - `@middleware` decorator
  - `@hookable` decorator (renamed from `@component`)
  - `Middleware`, `AsyncMiddleware` protocols
  - `execute_middleware()`, `execute_middleware_async()`
  - `execute_target_middleware()` (renamed from `execute_component_middleware()`)
  - `register_middleware()`, `register_hookable()`
  - `get_middleware_types()`, `AnyMiddleware`

## tdom-svcs Middleware (to be removed)

### Generic code (duplicates svcs-di):
- `src/tdom_svcs/middleware.py` - entire file
- `src/tdom_svcs/services/middleware/` - decorators, manager
- Generic types in `src/tdom_svcs/types.py`

### tdom-specific code (keeping):
- Path middleware in `src/tdom_svcs/services/path/`
- ARIA middleware in `examples/middleware/aria/`
- `COMPONENT_LOCATION_PROP` constant
- `DIContainer` protocol

## Tests Studied

- `tests/services/middleware/` - comprehensive generic middleware tests (delete entire directory)
- `tests/test_categories.py` - category integration tests (reduce to slim subset)
- `tests/test_component_middleware_storage.py` - storage tests (delete)

## Examples Studied

### Generic (deleting):
- `examples/middleware/basic/`
- `examples/middleware/dependencies/`
- `examples/middleware/scoping/`
- `examples/middleware/error_handling/`

### tdom-specific (updating):
- `examples/middleware/aria/` - accessibility checking
- `examples/middleware/path/` - path collection
- `examples/categories/` - category demonstration
