# Refactor for Inject Categories

## Context

tdom-svcs currently performs **duplicate module scanning**: once via `svcs_scan()` for `@injectable` services, then walks all modules again for `@middleware` and `@component` decorated classes. This duplicates `_get_all_modules()` / `_resolve_module()` logic that svcs-di already provides.

svcs-di now has **injectable categories** (`@injectable(categories=["middleware"])`) and a **subclassable `injectable` class** with hooks (`validate_target`, `build_metadata`, `post_decorate`). This lets us rewrite `@middleware` and `@component` as `injectable` subclasses, eliminating all duplicate scanning — svcs_scan() discovers everything in one pass.

### Assessment: Is Subclassing Worth It?

- **`middleware`** — clearly worth it. Becomes a one-liner subclass with `categories = ("middleware",)`. Eliminates the private `_tdom_middleware_` attribute marker entirely.
- **`component`** — worth it because it enables **single-pass scanning**. Requires overriding `__new__` to accept the `middleware` kwarg, and `post_decorate` to store the MiddlewareMap. The `component`-specific middleware config can't be expressed as a category alone, but the "component" category tag eliminates the need for a separate module-walking scan pass.

## Implementation Tasks

1. Save spec documentation
2. Rewrite `@middleware` as injectable subclass
3. Rewrite `@component` as injectable subclass
4. Simplify `scan()` — eliminate duplicate module walking
5. Update `__init__.py` exports
6. Update tests
7. Run verification checks

## Benefits

- **Single-pass scanning** — svcs_scan() discovers all injectables, middleware, and components in one pass
- **Eliminates ~140 lines of duplicate module-walking code**
- **Leverages svcs-di's category system** instead of custom metadata attributes
- **Preserves public API** — existing code continues to work unchanged
- **Better separation of concerns** — scanning logic lives in svcs-di where it belongs

## Trade-offs

- Requires svcs-di >= 2.5.0 (adds injectable categories)
- `@component` and `@middleware` become classes instead of functions (but still work as decorators)
- Component middleware config still needs post-scan registration step (can't be expressed as category alone)
