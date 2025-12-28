# Specification: tdom-svcs Integration Layer

## Goal
Create a wrapper around tdom's `html()` function in the tdom-svcs package that adds optional `config` and `context` parameters with pluggable protocols for component location and instantiation, enabling dependency injection capabilities while keeping tdom core unchanged.

## User Stories
- As a tdom user, I want to continue using `html()` without any parameters and have it work exactly as before
- As a tdom-svcs developer, I want to pass a config with component lookup logic and a context container to enable dependency injection during component resolution

## Specific Requirements

**Create html() wrapper function in tdom-svcs**
- Create new module `src/tdom_svcs/processor.py`
- Implement `html()` function that wraps `tdom.html()`
- Add two optional keyword-only parameters: `config: Config | None = None` and `context: Mapping[str, Any] | None = None`
- Maintain signature: `html(template: Template, *, config: Config | None = None, context: Mapping[str, Any] | None = None) -> Node`
- When config and context are None, pass through directly to `tdom.html()` (fast path)
- Import `Mapping` from `collections.abc` for flexible context typing
- Export from `src/tdom_svcs/__init__.py`

**Define Config Protocol in tdom-svcs**
- Create Protocol in `src/tdom_svcs/processor.py` with `component_lookup: ComponentLookup | None` attribute
- Use `@t.runtime_checkable` decorator for runtime type checking
- Protocol must be independent of svcs or svcs-di - no imports from those libraries
- Protocol allows structural subtyping - implementations don't need to inherit
- Place Protocol definition near top of processor.py after imports

**Define ComponentLookup Protocol in tdom-svcs**
- Protocol with `__init__(self, container: Any) -> None` method signature (use `Any` to avoid svcs dependency)
- Protocol with `__call__(self, name: str, context: Mapping[str, Any]) -> Callable | None` method signature
- Returns single callable (the component class/function) or None if not found
- Use `@t.runtime_checkable` decorator for runtime type checking
- Must remain completely independent of svcs-di types
- Designed to be implemented by HopscotchInjector in tdom-svcs but usable by any DI system
- Place Protocol definition in `src/tdom_svcs/processor.py`

**Implement component interception logic (future iteration)**
- NOTE: Initial implementation provides the wrapper and protocols only
- Component interception will be implemented in a future iteration
- For now, the wrapper passes through to tdom.html() regardless of config/context
- This establishes the API contract and allows building the rest of tdom-svcs

**Ensure tdom core remains unchanged**
- No modifications to tdom source code
- All changes confined to tdom-svcs package
- tdom remains a pure template processor with no DI awareness
- tdom-svcs wraps tdom to add DI capabilities
- Users can choose to use tdom directly or tdom-svcs for DI features

**Context parameter implementation**
- Type as `Mapping[str, Any]` from collections.abc for maximum flexibility
- Supports dict, ChainMap, or svcs.Container as implementations
- Mutable at application level (dict) but passed as immutable Mapping type
- Flows from html() -> _resolve_t_node() -> _invoke_component() -> ComponentLookup.__call__()
- No mutations within tdom - treated as read-only reference
- Available to ComponentLookup for service resolution

**Type safety and protocol patterns**
- Follow existing Protocol pattern from `HasHTMLDunder` (lines 36-38)
- Use `@t.runtime_checkable` decorator on all protocols
- Full type hints compatible with mypy and pyright
- Use `typing.Any` for container parameter to avoid external dependencies
- Import Mapping from collections.abc not typing
- Maintain existing import structure and ordering

**Component name extraction for lookup**
- Extract component name from interpolation value for ComponentLookup
- Use callable's `__name__` attribute if available, otherwise use `type(value).__name__`
- Pass this name as the `name` parameter to ComponentLookup.__call__()
- Fallback to original callable if name cannot be determined

**Documentation and examples**
- Add docstring to Config Protocol explaining its role in component resolution
- Add docstring to ComponentLookup Protocol with usage example
- Update html() docstring to document new config and context parameters
- Add inline comments in _invoke_component() explaining conditional ComponentLookup usage
- Include type hints in all signatures for IDE support

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**HasHTMLDunder Protocol pattern (processor.py lines 36-38)**
- Use as template for defining Config and ComponentLookup Protocols
- Apply same `@t.runtime_checkable` decorator
- Follow same structural typing approach without requiring inheritance
- Place new protocols near this existing one for consistency

**_invoke_component() function (processor.py lines 295-360)**
- Extend this function to add conditional ComponentLookup usage
- Preserve all existing logic: callable validation, kwargs building, children handling, signature checking
- Add new conditional branch before format_interpolation() that checks for config and component_lookup
- Keep existing error messages and exception types unchanged
- Maintain CallableInfo usage and validation patterns

**_resolve_t_node() recursive flow (processor.py lines 391-440)**
- Add config and context as optional parameters with None defaults
- Pass through to recursive calls for TFragment children (line 403-405)
- Pass through to TElement children (line 407-411)
- Pass through to TComponent handling (line 413-438)
- Pass to _invoke_component() at line 434-438
- Maintain existing pattern matching structure

**html() entry point (processor.py line 448)**
- Extend signature with keyword-only config and context parameters
- Pass to _resolve_t_node() call at line 452
- Keep existing caching logic with _parse_and_cache() unchanged
- Maintain same return type and behavior

**_substitute_and_flatten_children() helper (processor.py line 249)**
- Add config and context parameters to thread through to child resolution
- Update list comprehension at line 253 to pass parameters to _resolve_t_node()
- Maintain existing flattening logic unchanged

## Out of Scope
- Implementing actual injector classes like HopscotchInjector (belongs in tdom-svcs)
- Adding any svcs or svcs-di imports or dependencies to tdom core
- Caching or performance optimizations for component resolution
- Resource-based or location-based resolution logic (HopscotchInjector's responsibility)
- Middleware hooks or component lifecycle events (future roadmap feature #9)
- Changes to attribute handling or kebab-to-snake conversion logic
- Changes to children handling or flattening logic
- Testing utilities or mock injection helpers for consumers
- Integration with svcs.Container directly (handled by tdom-svcs layer)
- Multiple component candidate resolution or fallback chains (HopscotchInjector handles this)
- Async component resolution or async context support
