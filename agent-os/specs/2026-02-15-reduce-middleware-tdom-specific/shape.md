# Shaping Notes: Reduce Middleware to tdom-Specific Concerns

## Problem

svcs-di now contains generic middleware machinery (commit 8e2bc03) that was ported from tdom-svcs. tdom-svcs currently duplicates all of this generic code. This creates maintenance burden and violates DRY.

## Solution

Remove duplicated generic middleware code from tdom-svcs, keeping only tdom-specific integrations:
- Path collection and rewriting
- ARIA/accessibility checking
- Node tree operations

Re-export svcs-di middleware symbols for convenience.

## Appetite

Medium appetite (~6-8 hours). This is mechanical refactoring with clear boundaries.

## Rabbit Holes

- **Don't port examples back to svcs-di**: Generic examples should stay deleted; svcs-di has its own examples
- **Don't try to preserve backwards compatibility**: This is experimental research code; breaking changes are expected
- **Don't second-guess the plan**: The plan was shaped carefully with full context from reading both codebases

## No-Gos

- Don't modify svcs-di in this work
- Don't change tdom-svcs functionality beyond the refactoring
- Don't add new features or "improvements"

## Key Decisions

### Naming: `hookable` vs `component`

svcs-di uses `@hookable` for "things that can have middleware attached." tdom-svcs historically called these "components." We're adopting svcs-di's terminology:
- `@hookable` instead of `@component`
- `execute_target_middleware()` instead of `execute_component_middleware()`
- `"hookable"` category instead of `"component"` category

Rationale: Avoid maintaining parallel vocabularies. tdom-svcs users work with svcs-di concepts anyway.

### Re-exports from tdom-svcs

Users can import middleware symbols from either package:
```python
from tdom_svcs import hookable, execute_target_middleware  # re-exported
from svcs_di import hookable, execute_target_middleware    # original
```

Rationale: Convenience. Users shouldn't need to remember which package owns what.

### Test reduction philosophy

Delete all generic middleware tests. Keep only 5-8 integration tests that verify:
- Re-exports work correctly
- Category metadata flows through
- Introspection functions find middleware
- tdom-specific integrations function

Rationale: Generic middleware is now tested in svcs-di. Duplicating those tests adds no value.

## Out of Scope

- Improving middleware functionality
- Adding new tdom-specific middleware
- Documenting svcs-di middleware in detail (link to their docs instead)
- Porting tdom-svcs generic examples to svcs-di

## Success Criteria

1. All tests pass
2. Type checking passes
3. No imports from deleted modules remain
4. Documentation accurately reflects the new structure
5. Examples demonstrate tdom-specific middleware use cases
