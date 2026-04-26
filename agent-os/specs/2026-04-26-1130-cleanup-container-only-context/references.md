# References for Cleanup Container-Only Context

## Research and Specification

### Port to ian/integrations Research Doc

- **Location:** `docs/research/port-tstring-html-integrations.md`
- **Relevance:** Full architectural plan including Stage 1 (this item) specification
- **Key sections:**
  - Lines 24-41: Decisions locked in (container-only design)
  - Lines 97-118: Stage 1 scope and changes

## Source Files

### Types to Remove

- **Location:** `src/tdom_svcs/types.py`
- **Deletions:** `DIContainer` Protocol (lines 5-10), `is_di_container` TypeGuard (lines 13-17)
- **Impact:** This entire file is deleted; 18 lines total

### Processor Implementation

- **Location:** `src/tdom_svcs/processor.py`
- **Changes:** 8 targeted edits (lines 33, 35, 38, 49, 51, 150, 201, 211)
- **Scope:** No logic changes, only type annotations and guard replacements

### Test Files

- **Location:** `tests/test_html_wrapper.py`
- **Changes:** Simplify parametrize, remove dict-context cases
- **Lines affected:** 13-35

- **Location:** `tests/test_context_config_passing.py`
- **Changes:** Delete 4 tests (dict-specific), update 5 tests (dict → None), rename 5 calls (context= → container=)
- **Lines affected:** 11, 18-22, 25-42, 48-81, 113-139, 167-177, 181-200, 287-295

### Documentation

- **Location:** `docs/api_reference.md`
- **Changes:** Update `html()` signature on line 43
- **Change:** `context: DIContainer | dict[str, Any] | None = None` → `container: svcs.Container | None = None`

## Related Workspace Changes

### Depends On

- tstring-html `main` branch (current upstream, no new features needed for Stage 1)

### Feeds Into

- **Stage 2:** Template migration (components return `Template` instead of `str | Markup`)
- **Stage 3:** Port to ian/integrations branch with `_invoke_component` hook
- **Stage 4:** Workspace-wide adoption of tdom-svcs processor

## Roadmap Context

**Project:** tdom-svcs  
**Phase:** Phase 6 (Dependency Modernization) → Phase 7 (Port to Pluggable Component Processor)  
**Item:** 22 (Cleanup tdom-svcs Against Current Upstream)  
**Size:** S (small, ~1 day)  
**Priority:** Lowest risk, recommended before Stage 2 and Stage 3
