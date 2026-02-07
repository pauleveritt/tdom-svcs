# References: Injectable Categories Refactor

## svcs-di Documentation

- **Injectable categories**: https://github.com/hynek/svcs-di (check docs for category system)
- **Subclassable injectable**: Review `injectable.py` source for subclassing hooks

## Critical Files in tdom-svcs

### Before Refactor

- `src/tdom_svcs/middleware.py` — Current `@middleware` decorator implementation
- `src/tdom_svcs/services/middleware/decorators.py` — Current `@component` decorator
- `src/tdom_svcs/scanning.py` — 170+ lines of module walking and scanning logic
- `src/tdom_svcs/introspection.py` — `list_middlewares()`, `list_components()`

### Test Coverage

- `tests/test_introspection.py` — Tests middleware/component discovery
- `tests/services/middleware/test_middleware_manager.py` — Tests middleware execution
- `tests/services/middleware/test_hook_integration.py` — Tests component middleware
- `tests/services/middleware/test_integration_end_to_end.py` — Full integration tests

### Documentation

- `docs/services/` — Service layer documentation (may need updates)

## Related Work

- **Phase 2 completed**: Basic service layer with `@injectable` scanning
- **This refactor**: Eliminates duplicate scanning by leveraging svcs-di categories
- **Future work**: Consider whether other custom metadata can migrate to categories

## Implementation Order

1. Save spec documentation (this file and siblings)
2. Rewrite `@middleware` (simplest, no kwargs)
3. Rewrite `@component` (more complex, has middleware kwarg)
4. Simplify `scan()` (delete duplicate walking, add post-scan step)
5. Update tests (verify categories work, add integration test)
6. Verify with ty/ruff/pytest

## Verification Checklist

- [ ] `@middleware` sets `categories=("middleware",)` in metadata
- [ ] `@middleware` does NOT set `_tdom_middleware_` attribute
- [ ] `@component` sets `categories=("component",)` in metadata
- [ ] `@component` DOES set `_tdom_component_middleware_` attribute (needed for middleware config)
- [ ] `registry.get_by_category("middleware")` returns middleware types after scan
- [ ] `registry.get_by_category("component")` returns component types after scan
- [ ] `list_middlewares()` returns same results as before refactor
- [ ] `list_components()` returns same results as before refactor
- [ ] All existing tests pass
- [ ] No type errors from ty
- [ ] No lint errors from ruff
- [ ] `scanning.py` reduced from 170+ lines to ~30 lines
