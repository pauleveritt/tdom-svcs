# Spec Requirements: Core tdom Integration Hooks

## Initial Description

**Feature #1 from Product Roadmap**

Implement optional `config` and `context` parameters in tdom's `html()` function
- Design pluggable component location interface
- Design pluggable component instantiation interface
- Pass context through component lifecycle in processor
- Ensure backward compatibility with existing tdom usage

## Purpose

This is the foundation feature that enables all dependency injection capabilities by adding minimal, upstreamable changes to the tdom core library.

## Requirements Discussion

### First Round Questions

**Q1:** For the `config` and `context` parameters to `html()`, I'm assuming these should be optional keyword-only parameters (e.g., `html(..., *, config=None, context=None)`) to maintain backward compatibility. Is that correct, or should they use a different signature pattern?

**Answer:** Yes, optional keyword-only parameters (e.g., `html(..., *, config=None, context=None)`)

**Q2:** For the pluggable component location interface, I'm thinking this should be a Protocol or ABC with a method like `locate_component(name: str, context: Any) -> type | None`. Should the interface also support namespace/package-based lookups, or is simple name-based lookup sufficient for this foundation?

**Answer:** It should be a Protocol that matches a (frozen) dataclass that takes `container: Container` as an argument and the `__call__` does a `svcs-di` locator lookup.

**Q3:** For the pluggable component instantiation interface, I assume it should receive the component class, any props/kwargs, and the context, then return an instantiated component. Should this interface also handle validation of component initialization, or is that out of scope for the core hooks?

**Answer:** ComponentLookup protocol should only return the callable.

**Q4:** When passing context through the component lifecycle, I'm thinking context should flow from `html()` -> processor -> component location -> component instantiation. Should context be immutable (frozen dataclass/namedtuple) or mutable (dict-like) to allow modifications during the lifecycle?

**Answer:** Mutable (dict-like)

**Q5:** For backward compatibility, I assume existing tdom code that doesn't pass `config` or `context` should work exactly as before with no behavioral changes. Should there be any deprecation warnings, or should the old behavior be permanently supported?

**Answer:** Yes, existing `html()` calls should work exactly as before.

**Q6:** I'm thinking the pluggable interfaces should be defined as Protocols (PEP 544) for structural subtyping rather than requiring inheritance from base classes. Does this align with tdom's architecture philosophy?

**Answer:** Yes, use Protocols

**Q7:** For the component location interface, should it support returning multiple candidates (for fallback chains) or just a single component class? This would affect whether HopscotchInjector needs to be implemented in tdom-svcs or if the foundation should support it.

**Answer:** Single component return, use HopscotchInjector locator

**Q8:** What should be explicitly excluded from this feature? For example: should we avoid any svcs-specific logic, skip implementing actual injector classes (leave that to tdom-svcs), or exclude any caching/performance optimizations at this stage?

**Answer:** None.

### Follow-up Questions

**Follow-up 1:** You mentioned the ComponentLookup protocol should match a frozen dataclass that takes `container: Container` as an argument and the `__call__` does a svcs-di locator lookup. Should this be: a Protocol with `__init__(self, container: Container)` and `__call__(self, name: str, context: dict) -> Callable | None`, or a different signature?

**Answer:** Yes, Protocol with `__init__(self, container: Container)` and `__call__(self, name: str, context: dict) -> Callable | None` looks good.

**Follow-up 2:** When you say "the protocol should be independent of svcs-di", should tdom remain completely independent of svcs-di? Should the protocol be generic enough that tdom core has no svcs-di imports or type references?

**Answer:** The protocol should be independent of svcs-di. Tdom should remain completely independent.

**Follow-up 3:** For the `config` parameter in `html()`, what type should it be? Should it be typed as `Any`, a Protocol defining required methods, or something else? What will config actually contain?

**Answer:** Should be a Protocol with defined members.

**Follow-up 4:** For context being dict-like, should it be literally a `dict[str, Any]`, or should it support any MutableMapping, or should there be a Context Protocol?

**Answer:** It should be an abstract mapping (like `Mapping` from collections.abc) that could be satisfied by a dict, ChainMap, or svcs.Container.

**Follow-up 5:** You mentioned using "HopscotchInjector locator" - should the tdom core hooks be aware of this name/concept, or should tdom just define generic protocols that HopscotchInjector will implement later in tdom-svcs?

**Answer:** HopscotchInjector should be able to be plugged in, or left out. Tdom should just define generic protocols.

**Follow-up 6:** Could you point me to the current tdom codebase location?

**Answer:** `../tdom` (relative to the current project at `/Users/pauleveritt/projects/t-strings/tdom-svcs/`)

### Existing Code to Reference

**Current tdom Implementation:**
- Main module: `/Users/pauleveritt/projects/t-strings/tdom/tdom/__init__.py`
- Processor with `html()` function: `/Users/pauleveritt/projects/t-strings/tdom/tdom/processor.py`
- Existing Protocol usage: `HasHTMLDunder` Protocol in processor.py (line 36-38)
- Component invocation: `_invoke_component()` function (lines 295-360) handles current component resolution and instantiation

**svcs-di Implementation (for understanding target integration):**
- ServiceLocator and HopscotchInjector: `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/locator.py`
- HopscotchInjector (lines 510-648): Takes `container: svcs.Container` in `__init__`, implements `__call__[T](self, target: type[T], **kwargs: Any) -> T`
- This will be the primary consumer of the tdom hooks

**Key Architectural Patterns:**
- tdom already uses Protocol pattern for `HasHTMLDunder`
- Current component resolution in `_invoke_component()` uses direct callable invocation
- tdom processor flows: `html()` -> `_resolve_t_node()` -> `_invoke_component()` for components
- Component attributes are converted from kebab-case to snake_case before invocation

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
No visual assets available for analysis.

## Requirements Summary

### Functional Requirements

**1. Extend `html()` function signature:**
- Add optional keyword-only parameters: `config` and `context`
- New signature: `html(template: Template, *, config: Config | None = None, context: Mapping[str, Any] | None = None) -> Node`
- Maintain complete backward compatibility - existing calls without these parameters must work identically

**2. Define Config Protocol:**
- Create a Protocol that defines the structure and methods of the config object
- Config should contain the component lookup implementation
- Protocol should have defined members (to be specified based on what tdom-svcs needs)
- Must remain independent of svcs or svcs-di

**3. Define ComponentLookup Protocol:**
- Protocol with `__init__(self, container: Container)` signature
- Protocol with `__call__(self, name: str, context: Mapping[str, Any]) -> Callable | None` signature
- Must be independent of svcs-di types (use generic Container reference or avoid dependency)
- Single component return (not multiple candidates)
- Designed to be satisfied by HopscotchInjector from svcs-di

**4. Context parameter specification:**
- Type: `Mapping[str, Any]` from collections.abc
- Mutable and flexible enough to be satisfied by dict, ChainMap, or svcs.Container
- Flows through component lifecycle: `html()` -> processor -> component resolution -> component instantiation

**5. Component lifecycle integration:**
- Pass `config` and `context` through processor's `_resolve_t_node()` flow
- Modify `_invoke_component()` to optionally use ComponentLookup from config when available
- If config is None or ComponentLookup not provided, use existing behavior (direct callable invocation)
- Context should be available to ComponentLookup during resolution

**6. Backward compatibility:**
- All existing tdom code must work without changes
- No behavioral changes when config/context are not provided
- No deprecation warnings - old behavior is permanent
- Existing component invocation logic remains as fallback

### Reusability Opportunities

**Existing tdom patterns to follow:**
- Protocol pattern: Follow `HasHTMLDunder` Protocol example (processor.py lines 36-38)
- Component invocation: Extend existing `_invoke_component()` logic (processor.py lines 295-360)
- Processor flow: Integrate with existing `_resolve_t_node()` tree traversal (processor.py lines 391-440)
- Caching pattern: Consider relationship with existing `_parse_and_cache()` pattern (processor.py lines 46-48)

**Integration targets (in tdom-svcs):**
- HopscotchInjector from svcs-di will implement ComponentLookup Protocol
- ServiceLocator will be used by HopscotchInjector for multi-implementation resolution
- svcs.Container will be passed as context parameter

### Scope Boundaries

**In Scope:**
- Add optional `config` and `context` parameters to `html()` function
- Define Config Protocol with required members
- Define ComponentLookup Protocol (independent of svcs-di)
- Pass config and context through processor's component resolution flow
- Modify `_invoke_component()` to optionally use ComponentLookup when available
- Maintain 100% backward compatibility
- Type annotations using Protocols
- Documentation of the new parameters and protocols

**Out of Scope:**
- Implementing actual injector classes (that's tdom-svcs responsibility)
- Any svcs or svcs-di dependencies in tdom core
- Caching or performance optimizations for component resolution
- Resource-based or location-based resolution logic (that's HopscotchInjector's job)
- Changes to component attribute handling (kebab-to-snake conversion)
- Changes to children handling logic
- Testing utilities or mock injection helpers
- Integration with svcs.Container (handled by tdom-svcs)

**Future Enhancements (not in this feature):**
- Component lifecycle middleware hooks (roadmap item #9)
- Performance optimization and caching (roadmap item #10)
- Multiple implementation support (handled by HopscotchInjector in tdom-svcs)

### Technical Considerations

**Type safety:**
- Use Protocol for structural typing (PEP 544)
- Full type hints with mypy/pyright compatibility
- Context typed as `Mapping[str, Any]` for flexibility
- Config typed as Protocol with specific members

**Independence from svcs:**
- tdom core must have NO imports from svcs or svcs-di
- Protocols should be generic enough for any DI system
- Container reference in ComponentLookup should be generic or avoided via Protocol

**Integration points:**
- `html()` function signature extension (processor.py line 448)
- `_resolve_t_node()` needs to receive and pass config/context (processor.py line 391)
- `_invoke_component()` needs conditional ComponentLookup usage (processor.py line 295)
- TComponent handling in pattern matching (processor.py lines 413-438)

**Backward compatibility strategy:**
- Default values: `config=None, context=None`
- Conditional logic: only use new behavior when config is not None
- Fallback: existing component invocation when ComponentLookup not available
- No changes to existing function signatures except `html()`

**Existing constraints:**
- Python 3.14+ (PEP 750 t-strings)
- Must work with existing tdom caching strategy
- Must maintain current component invocation rules (keyword-only args, children handling)
- Must preserve existing error messages and exception types
