# Spec Requirements: @Inject Decorator and Component Discovery

## Initial Description

Implement @Inject decorator to mark injectable components, create package scanning utility to discover decorated components, and register them with the injector.

**Size:** M (Medium)

**Roadmap Context:** This is the third item in the tdom-svcs product roadmap, building on the foundation of tdom hooks (Item 1, completed) and svcs container integration (Item 2, pending).

## Requirements Discussion

### First Round Questions

**Q1:** I assume the `@Inject` decorator should support both class-based components and function-based components (similar to how tdom works). Is that correct, or should we start with just one type?

**Answer:** Just class-based components (svcs-di relies on types). Raise a friendly exception if applied to a function.

**Q2:** For component discovery, I'm thinking we should use a package scanning approach where developers explicitly specify which packages to scan (e.g., `discover_components("myapp.components")`), rather than auto-scanning all imports. Should we provide this explicit scanning API, or would you prefer automatic discovery based on imports?

**Answer:** User requested more information about reusing svcs-di's decorator implementation before answering fully.

**Q3:** I assume the decorator should capture type hints from the component's parameters to determine what services need to be injected. For example:
```python
@Inject
def MyButton(label: str, db: DatabaseService) -> Tag:
    ...
```
Here, `label` would be a regular prop, while `db: DatabaseService` would be injected from the container. Is this the right approach, or should we use a different mechanism to distinguish injected dependencies from regular props?

**Answer:** Only inject if the parameter is wrapped with `Inject[]` (from svcs-di).

**Q4:** For registration with the injector, I'm thinking decorated components should be registered by their component type (the decorated callable itself) as the lookup key. Should we also support registering by a string name or interface type for multi-implementation scenarios, or keep it simple with just the component type for now?

**Answer:** Yes, type-based registration.

**Q5:** Should the `@Inject` decorator accept any configuration parameters (like scope, aliases, or registration hints), or should it be a simple marker decorator with no arguments?

**Answer:** It should accept the same arguments as the `@injectable` decorator and have the same kind of effect. Only difference is the parallel str -> type lookup. Once you have the type, use the normal svcs-di lookup.

**Q6:** For error handling during package scanning, I assume we should fail fast if a specified package doesn't exist or can't be imported, but continue scanning if an individual module within the package has import errors (with a warning). Is that the right balance?

**Answer:** Yes - fail fast if package doesn't exist, warn for individual module import errors.

**Q7:** I'm thinking the component discovery process should happen at application startup (when the injector is initialized), not lazily at first use. Should discovery be explicit/eager, or would you prefer lazy discovery when components are first referenced?

**Answer:** Scanner allows a configuration phase after import-time.

**Q8:** Is there anything you explicitly want to exclude from this feature? For example, should we defer runtime validation of injectable dependencies, hot-reloading of discovered components, or advanced filtering/exclusion rules for package scanning?

**Answer:** No exclusions needed.

### Decorator Reuse Discussion

**User Question:** "Let's re-use decorator.py from svcs-di, unless there is a good reason not to? Tell me more about this."

**Analysis Provided:** After analyzing svcs-di's `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/decorators.py`, I explained that the existing `@injectable` decorator provides:
- Dual syntax support (bare and parameterized)
- Metadata storage for `for_`, `resource`, and `location` parameters
- Deferred registration pattern (decorator marks, scan() registers)
- Package scanning integration with error handling

**Recommendation:** Use Option A (direct reuse) - import and use `@injectable` decorator as-is from svcs-di, then create a new `scan_components()` function in tdom-svcs that leverages svcs-di's scanning infrastructure and adds string name mappings to ComponentNameRegistry.

**User Decision:** Option A is good - use direct reuse of svcs-di's `@injectable` decorator (no wrapper, no duplication).

### Follow-up Questions

**Follow-up 1:** Should the string name for `ComponentNameRegistry` always be the class's `__name__`, or should we allow overriding it with an optional parameter like `@injectable(name="CustomName")`?

**Answer:** Use `__name__` (class name) always, no override parameter.

**Follow-up 2:** When you say "scanner allows a configuration phase after import-time", do you mean developers call `scan_components()` explicitly in their app startup code, OR tdom-svcs provides a configuration helper that collects package names and scans them all at once?

**Answer:** First bullet - developers call `scan_components()` explicitly in their app startup code once they have a registry created. Scanning needs a registry instance.

**Follow-up 3:** When `@injectable` is applied to a function (which you want to disallow), should we raise the error immediately at decoration time (when the decorator is applied), OR raise it during scanning (when `scan_components()` discovers it)?

**Answer:** Raise the error as early as possible (at decoration time when decorator is applied).

**Follow-up 4:** Should components be registered in `ComponentNameRegistry` first, then svcs container (type-based), OR svcs container first (via svcs-di's scan), then extract and add to `ComponentNameRegistry`?

**Answer:** Whichever is best (implementer should decide based on what's most logical).

### Existing Code to Reference

**Similar Features Identified:**

- **svcs-di decorator system:** `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/decorators.py`
  - Contains `@injectable` decorator implementation with dual syntax support
  - Stores metadata via `__injectable_metadata__` attribute
  - Pattern to reuse directly (no duplication)

- **svcs-di scanning infrastructure:** `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/locator.py`
  - Contains `scan()` function starting at line 1002
  - Package traversal with error handling
  - Auto-detection of caller's package
  - Registration to ServiceLocator or Registry based on metadata

- **ComponentNameRegistry:** `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/services/component_registry/component_name_registry.py`
  - Thread-safe registry for string name → type mapping
  - Existing `register(name, component_type)` and `get_type(name)` methods
  - Used by ComponentLookup to resolve component names from tdom templates

- **tdom-svcs architecture:** `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/`
  - Current integration between tdom and svcs via `processor.py`
  - Service-based architecture with ComponentLookup
  - Foundation for adding component discovery

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable.

## Requirements Summary

### Functional Requirements

**Core Functionality:**
- Reuse svcs-di's `@injectable` decorator directly (no wrapper, no new decorator)
- Create validation wrapper or check that raises friendly error if `@injectable` is applied to a function (not a class)
- Error should be raised at decoration time (as early as possible)
- Create `scan_components()` function that:
  - Accepts `registry` (svcs.Registry), `component_name_registry` (ComponentNameRegistry), and package names
  - Leverages svcs-di's existing `scan()` infrastructure for package traversal and discovery
  - Registers discovered components in both registries (dual registration)
  - Uses class `__name__` as string name (no override mechanism)

**Decorator Behavior:**
- Support same arguments as svcs-di's `@injectable`: `for_`, `resource`, `location`
- Store metadata on decorated classes for later registration
- Only mark classes - defer actual registration to `scan_components()`
- Work seamlessly with svcs-di's dependency injection system

**Component Resolution:**
- String name lookup: "Button" → `ButtonComponent` type (via ComponentNameRegistry)
- Type-based DI: `ButtonComponent` → resolved instance with `Inject[]` parameters injected (via svcs container)
- Parameters wrapped with `Inject[]` are injected from container
- Regular parameters are passed as props from template

**Scanning and Discovery:**
- Explicit scanning API: developers call `scan_components(registry, component_name_registry, "package.name")` at app startup
- Package scanning discovers all `@injectable` decorated classes
- Configuration happens after import-time (explicit developer control)
- Support multiple package arguments: `scan_components(registry, cnr, "app.components", "app.ui")`

**Error Handling:**
- Fail fast: If specified package doesn't exist or can't be imported, raise error immediately
- Warn and continue: If individual module within package has import errors, log warning and continue scanning
- Friendly error: If `@injectable` applied to function (not class), raise clear error at decoration time
- Error messages should suggest available component names when lookup fails

**Registration Strategy:**
- Dual registration: Components registered in both ComponentNameRegistry (by string name) and svcs container (by type)
- Registration order: Use most logical approach (likely svcs container first via scan, then extract for ComponentNameRegistry)
- Type-based registration enables normal svcs-di dependency resolution
- String name registration enables tdom template resolution

### Reusability Opportunities

**Direct Code Reuse:**
- `@injectable` decorator from svcs-di (zero duplication)
- `scan()` function infrastructure from svcs-di (package traversal, error handling, metadata processing)
- ServiceLocator registration logic for resource/location-based components
- ComponentNameRegistry.register() for string name mappings

**Patterns to Follow:**
- Deferred registration pattern (decorator marks, scan function registers)
- Metadata storage via class attributes (`__injectable_metadata__`)
- Thread-safe registry operations (as in ComponentNameRegistry)
- Error handling during import/scanning (fail fast vs. warn and continue)

**Integration Points:**
- svcs.Registry for type-based service registration
- ComponentNameRegistry for string name → type mappings
- ComponentLookup for template component resolution
- svcs-di's injector system for dependency resolution

### Scope Boundaries

**In Scope:**
- Reusing svcs-di's `@injectable` decorator with validation for class-only usage
- Creating `scan_components()` function with explicit API
- Package scanning infrastructure leveraging svcs-di's implementation
- Dual registration (ComponentNameRegistry + svcs container)
- String name derivation from class `__name__`
- Support for `for_`, `resource`, `location` parameters
- Error handling (fail fast for packages, warn for modules)
- Decoration-time validation for function usage
- Integration with existing ComponentNameRegistry and ComponentLookup

**Out of Scope:**
- Custom component name overrides (always use `__name__`)
- Wrapper decorator around `@injectable`
- Automatic/lazy discovery without explicit scan call
- Hot-reloading of components
- Advanced filtering/exclusion rules during scanning
- Runtime validation of injectable dependencies (defer to future)
- Function-based component support
- Auto-scanning all imports without package specification

**Future Enhancements:**
- Runtime dependency validation
- Hot-reloading capabilities
- Advanced scanning filters
- Component name customization
- Development tooling for component discovery debugging

### Technical Considerations

**Dependencies:**
- svcs-di: Provides `@injectable` decorator and `scan()` function
- svcs: Provides Registry and Container for DI
- tdom: Provides component system and template rendering
- Python 3.14+: Required for t-strings and type system

**Integration Points:**
- Import and re-export `injectable` from `svcs_di.injectors.decorators`
- Call `scan()` from `svcs_di.injectors.locator` within `scan_components()`
- Register to `ComponentNameRegistry` for string name lookup
- Register to svcs.Registry for type-based DI
- Work with existing ComponentLookup service

**Type Safety:**
- Components must be classes (enforced at decoration time)
- Full mypy/pyright support via svcs-di's type stubs
- `Inject[T]` provides type hints for injected dependencies
- ComponentNameRegistry maintains type information

**Thread Safety:**
- ComponentNameRegistry uses threading.Lock (already implemented)
- svcs.Registry is thread-safe
- Scanning should happen during single-threaded startup phase

**Error Handling Strategy:**
- Decoration time: Validate decorator applied to class, not function
- Package resolution: Fail fast if package doesn't exist
- Module import: Warn and continue if individual module fails
- Component lookup: Suggest available names on ComponentNameRegistry misses

**Testing Considerations:**
- Test decorator validation (class vs. function)
- Test package scanning with valid/invalid packages
- Test dual registration (both registries updated)
- Test component resolution via string name → type → instance
- Test error handling (fail fast vs. warn)
- Test `Inject[]` parameter resolution
- Test integration with existing ComponentLookup

**Performance:**
- Scanning happens once at startup (explicit call)
- ComponentNameRegistry uses dict lookup (O(1))
- svcs container uses efficient type-based lookup
- No lazy loading or dynamic discovery overhead

**Documentation Needs:**
- How to use `@injectable` on component classes
- How to call `scan_components()` at app startup
- How `Inject[]` parameters work vs. regular props
- Error messages and troubleshooting guide
- Examples of resource/location-based component registration
- Migration guide from manual ComponentNameRegistry.register() calls
