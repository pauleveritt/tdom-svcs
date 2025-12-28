# Architecture Change: tdom-svcs Wrapper Approach

## Summary

**Date:** 2025-12-28
**Decision:** Move all implementation from tdom core to tdom-svcs package

## Previous Approach (Reverted)

Initially, the implementation added hooks directly to tdom's core `processor.py` file:

- Modified `html()` function to accept `config` and `context` parameters
- Modified `_resolve_t_node()`, `_substitute_and_flatten_children()`, and `_invoke_component()`
- Added ComponentLookup and Config protocols to tdom core
- Threaded parameters through the entire processing pipeline

**Location:** `/Users/pauleveritt/projects/t-strings/tdom/tdom/processor.py`

## New Approach (Current)

The implementation now creates a wrapper layer in tdom-svcs:

- **tdom core remains completely unchanged**
- `tdom-svcs` provides its own `html()` function that wraps `tdom.html()`
- ComponentLookup and Config protocols defined in tdom-svcs
- Component interception logic will be implemented in tdom-svcs (future iteration)

**Location:** `src/tdom_svcs/processor.py`

## Rationale

1. **Separation of Concerns**: tdom remains a pure template processor with no DI awareness
2. **Cleaner Dependencies**: tdom has no knowledge of dependency injection concepts
3. **User Choice**: Users can use tdom directly or opt into tdom-svcs for DI features
4. **Simpler Maintenance**: Changes to DI logic don't require modifying tdom core
5. **Better Testing**: DI features can be tested independently from tdom core

## What Was Moved

### Code Files

- `src/tdom_svcs/processor.py` - ComponentLookup and Config protocols, html() wrapper
- `src/tdom_svcs/__init__.py` - Updated to export ComponentLookup, Config, html

### Test Files

- `tests/test_protocols.py` - Protocol structural typing tests (4 tests)
- `tests/test_html_wrapper.py` - html() wrapper tests (6 tests)

### Reverted from tdom

- All modifications to `/Users/pauleveritt/projects/t-strings/tdom/tdom/processor.py`
- All test files added to tdom (processor_*_test.py files)

## Current Status

✅ **Complete:**

- tdom core reverted to clean state (no modifications)
- Protocols defined in tdom-svcs
- html() wrapper created in tdom-svcs
- 10 tests passing in tdom-svcs
- Spec updated to reflect new architecture

⏳ **Future Work:**

- Implement actual component interception logic in tdom-svcs
- Add ComponentLookup implementation using svcs/svcs-di
- Build out full DI integration in tdom-svcs

## Implementation Details

The current tdom-svcs `html()` wrapper:

```python
def html(
        template: Template,
        *,
        config: Config | None = None,
        context: Mapping[str, t.Any] | None = None,
) -> Node:
    if config is None and context is None:
        # Fast path: no DI, just use tdom directly
        return tdom_html(template)

    # Component interception logic will be added here
    return tdom_html(template)
```

This establishes the API contract and allows building the rest of tdom-svcs while keeping tdom clean.

## Migration Impact

- **tdom users:** No impact - tdom unchanged
- **tdom-svcs users:** Will import from `tdom_svcs` instead of `tdom`
- **Test suite:** All tests moved to tdom-svcs, all passing

## Files Changed in This Repository (tdom-svcs)

**Created:**

- `src/tdom_svcs/processor.py`
- `tests/test_protocols.py`
- `tests/test_html_wrapper.py`
- `agent-os/specs/2025-12-27-core-tdom-integration-hooks/ARCHITECTURE_CHANGE.md`

**Modified:**

- `src/tdom_svcs/__init__.py`
- `agent-os/specs/2025-12-27-core-tdom-integration-hooks/spec.md`

**No changes to tdom repository** ✅
