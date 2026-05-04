# Standards: Injectable Categories Refactor

## Relevant Standards

### svcs-di: Injectable Categories (svcs-di >= 2.5.0)

**Source:** svcs-di documentation, injectable.py source code

**Key Principles:**
- `@injectable(categories=["foo"])` tags an injectable with semantic categories
- `registry.get_by_category("foo")` retrieves all injectables in that category
- `registry._register_categories(target, ["foo"])` imperatively adds categories
- Categories are stored in `__injectable_metadata__.categories` tuple
- Multiple categories allowed per injectable

**Application:**
- Use `categories=("middleware",)` for middleware types
- Use `categories=("component",)` for component types
- Replace custom `MIDDLEWARE_REGISTRY_KEY` with category-based lookup
- Replace custom `MIDDLEWARE_METADATA_ATTR` marker with category membership

### svcs-di: Subclassable Injectable

**Source:** svcs-di injectable.py source code

**Key Principles:**
- `injectable` can be subclassed to create specialized decorators
- Override `validate_target(target)` to enforce constraints
- Override `build_metadata(target, metadata)` to add custom metadata
- Override `post_decorate(target, metadata)` to run post-decoration hooks
- Subclass `__new__` allows accepting custom kwargs (like `middleware=`)

**Application:**
- Subclass `injectable` for `middleware` decorator
- Subclass `injectable` for `component` decorator
- Use `post_decorate` to store `COMPONENT_MIDDLEWARE_ATTR` after decoration
- Use `__new__` to capture `middleware=` kwarg before decoration
- Set `categories` as class attribute on subclass

### Python: Decorator Classes

**Source:** Python language reference

**Key Principles:**
- Class with `__new__` and `__call__` can act as decorator
- Bare usage `@decorator` calls class without arguments
- Parameterized usage `@decorator(args)` calls class with arguments, returns decorator
- Must handle both bare and parameterized forms in `__new__`

**Application:**
- `@middleware` (bare) → `middleware.__new__(cls, target=None)` → decorates immediately
- `@component(middleware={})` (parameterized) → `component.__new__(cls, target=None, middleware={})` → returns instance → instance decorates target
- Preserve backward compatibility with existing usage patterns

### tdom-svcs: Single-Pass Scanning

**Design Principle:** Minimize redundant module walking

**Key Principles:**
- svcs-di's `svcs_scan()` already walks all modules and discovers `@injectable` decorations
- Don't duplicate module walking for middleware/component discovery
- Use categories to tag middleware/components during decoration
- Post-scan step only for operations that require full registry (like component middleware registration)

**Application:**
- Delete `_resolve_module()`, `_get_all_modules()`, `_scan_for_middleware()`, `_scan_for_component_middleware()`
- Let `svcs_scan()` discover all `@injectable`, `@middleware`, `@component` in one pass
- Add minimal `_register_component_middlewares()` post-scan step
- Reduce `scanning.py` from 170+ lines to ~30 lines

### tdom-svcs: API Stability

**Design Principle:** Preserve public API across refactorings

**Key Principles:**
- Existing user code should not break
- Decorator usage patterns must remain unchanged
- Introspection functions must return same results
- Internal implementation can change freely

**Application:**
- Keep `@middleware`, `@component` decorator syntax identical
- Keep `register_middleware()`, `register_component_middleware()` imperative APIs
- Keep `list_middlewares()`, `list_components()` introspection APIs
- Implementation switches from custom metadata to categories under the hood
