# tdom-svcs Research Results

## Executive Summary

This document summarizes research on integrating **tdom** (Template DOM for Python 3.14 t-strings) with **svcs-di** (
dependency injection using svcs). The goal is to enable dependency injection for tdom components while maintaining
minimal, upstreamable changes to the core tdom library.

## Current State Analysis

### tdom (Template DOM Library)

**Location**: `~/projects/t-strings/tdom`

**Current Architecture**:

- Pure function-based HTML templating using Python 3.14 t-strings
- Main entry point: `html(template: Template) -> Node`
- Parser converts t-string templates to `TNode` tree structures
- Processor resolves interpolations and creates final `Node` tree
- No dependency injection or component system currently implemented

**Key Files**:

- `tdom/processor.py`: Core `html()` function and node resolution logic
- `tdom/parser.py`: Template parsing and AST generation
- `tdom/nodes.py`: Node types (Element, Text, Fragment, etc.)

**Current `html()` Signature**:

```python
def html(template: Template) -> Node:
    """Parse an HTML t-string, substitute values, and return a tree of Nodes."""
```

### svcs-di (Dependency Injection Library)

**Location**: `~/projects/t-strings/svcs-di`

**Architecture**:

- Thin layer on top of the `svcs` service container library
- Provides automatic dependency resolution based on type hints
- Explicit opt-in via `Inject[T]` type marker
- Multiple injector implementations with different capabilities

**Key Exports**:

- `auto()` / `auto_async()`: Factory generators for automatic injection
- `Inject[T]`: Type marker for parameters to be injected
- `DefaultInjector`: Basic dependency injection from container
- `KeywordInjector`: Adds kwargs override support (three-tier precedence)
- `HopscotchInjector`: Multi-implementation resolution (resource/location-based)
- `@Inject`: Decorator for auto-discovery and scanning

**Injector Hierarchy**:

1. **DefaultInjector** - Two-tier resolution:
    - Container services (`Inject[T]`)
    - Parameter defaults

2. **KeywordInjector** - Three-tier resolution:
    - kwargs overrides (highest priority)
    - Container services (`Inject[T]`)
    - Parameter defaults (lowest priority)

3. **HopscotchInjector** - Context-aware resolution:
    - Extends `KeywordInjector` with `ServiceLocator` support
    - Resource-based selection (e.g., `EmployeeContext` vs `CustomerContext`)
    - Location-based selection (hierarchical URL paths)
    - LIFO registration ordering

**Example Usage**:

```python
@dataclass
class Service:
    db: Inject[Database]  # Injected from container
    timeout: int = 30  # Uses default value


registry = svcs.Registry()
registry.register_factory(Database, Database)
registry.register_factory(Service, auto(Service))

container = svcs.Container(registry)
service = container.get(Service)  # db automatically injected
```

## Integration Goals

### Minimal tdom Changes (Upstreamable)

The research identified these minimal changes needed for tdom:

1. **Optional `config` argument** to `html()`:
    - Frozen dataclass instance
    - Contains tdom-managed configuration
    - No specific policy enforced

2. **Optional `context` argument** to `html()`:
    - Dict-like interface (matches svcs container API)
    - Passed through component lifecycle
    - No dependency injection logic in core tdom

3. **Pluggable component location**:
    - Customizable strategy for finding components
    - Receives context as argument
    - Default implementation provided

4. **Pluggable component instantiation**:
    - Customizable strategy for creating component instances
    - Receives context as argument
    - Enables dependency injection at instantiation time

**Proposed `html()` Signature**:

```python
def html(
        template: Template,
        config: Optional[FrozenConfig] = None,
        context: Optional[Mapping[type, Any]] = None,
) -> Node:
    """Parse an HTML t-string with optional configuration and context."""
```

### tdom-svcs Policy Layer (Not Upstreamed)

This package provides opinionated policies built on the minimal tdom changes:

1. **svcs container integration**: Use svcs `Container` as the context
2. **Component injection**: Use svcs-di injectors for component instantiation
3. **Multiple implementations**: Support `HopscotchInjector` for alternate component registrations
4. **Decorator-based discovery**: Use `@Inject` for component scanning

## Use Cases to Demonstrate

Based on the research goals in `research.md`, the following examples should be implemented:

### 1. Basic Container Injection

**Injector**: `DefaultInjector`

Inject the svcs `Container` itself into a component:

```python
@dataclass
class MyComponent:
    container: Inject[svcs.Container]

    def render(self):
        # Can get services directly
        db = self.container.get(Database)
        return html(t"<div>Connected to {db.host}</div>")
```

### 2. Service Injection

**Injector**: `DefaultInjector`

Inject specific services from container:

```python
@dataclass
class MyComponent:
    db: Inject[Database]
    cache: Inject[Cache]
    title: str = "Default"

    def render(self):
        return html(t"<h1>{self.title}</h1>")
```

### 3. Component Props with Kwargs

**Injector**: `KeywordInjector`

Override dependencies and pass component "props":

```python
# Template usage
html(t"<MyComponent title='Custom' timeout=60 />", context=container)


# Component receives both injected services and props
@dataclass
class MyComponent:
    db: Inject[Database]  # From container
    title: str = "Default"  # From kwargs or default
    timeout: int = 30  # From kwargs or default
```

### 4. Multi-Implementation Resolution

**Injector**: `HopscotchInjector`

Select component implementations based on context:

```python
@Inject(for_=Greeting)
@dataclass
class DefaultGreeting:
    salutation: str = "Hello"


@Inject(for_=Greeting, resource=EmployeeContext)
@dataclass
class EmployeeGreeting:
    salutation: str = "Hey"


# In template - resolves to different implementation based on context
html(t"<Greeting name='Alice' />", context=container)
```

### 5. Location-Based Resolution

Select components based on URL paths:

```python
@Inject(for_=Header, location=PurePath("/admin"))
@dataclass
class AdminHeader:
    title: str = "Admin Dashboard"


# Different header for /admin vs /public
registry.register_value(Location, PurePath("/admin"))
html(t"<Header />", context=container)
```

## Technical Considerations

### Component Lifecycle Integration Points

1. **Component Discovery** (pluggable):
    - How to find component class from name in template
    - Default: simple name-to-class lookup
    - Could support: module scanning, naming conventions, etc.

2. **Component Instantiation** (pluggable):
    - How to create component instance
    - Default: simple constructor call
    - With svcs-di: Use `auto()` wrapper with injector

3. **Component Rendering**:
    - How to get HTML from component
    - Could call `.render()` method
    - Could use `__html__()` protocol

### Architecture Layers

```
┌─────────────────────────────────────────────────┐
│  tdom-svcs (Policy Layer)                       │
│  - svcs container integration                    │
│  - DefaultInjector / KeywordInjector config     │
│  - HopscotchInjector with ServiceLocator        │
│  - @Inject decorator support                 │
└─────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│  tdom (Core Library - Upstreamable)             │
│  - html(template, config, context)              │
│  - Pluggable component location                  │
│  - Pluggable component instantiation            │
│  - No DI logic in core                          │
└─────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│  svcs-di (Dependency Injection)                 │
│  - auto() factory generators                     │
│  - Inject[T] marker                         │
│  - Multiple injector implementations            │
└─────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Core tdom Modifications

- [ ] Add optional `config` and `context` parameters to `html()`
- [ ] Design pluggable component location interface
- [ ] Design pluggable component instantiation interface
- [ ] Update processor to pass context through component lifecycle
- [ ] Add tests for new parameters

### Phase 2: tdom-svcs Integration Layer

- [ ] Implement svcs container adapter for tdom context
- [ ] Create component locator using svcs registry
- [ ] Create component instantiator using svcs-di injectors
- [ ] Support DefaultInjector for basic injection
- [ ] Add configuration helpers

### Phase 3: Advanced Injectors

- [ ] Integrate KeywordInjector for props support
- [ ] Integrate HopscotchInjector with ServiceLocator
- [ ] Support resource-based component resolution
- [ ] Support location-based component resolution

### Phase 4: Developer Experience

- [ ] Add `@Inject` decorator support for components
- [ ] Implement component scanning utilities
- [ ] Create comprehensive examples
- [ ] Write documentation
- [ ] Add type stubs for better IDE support

## Open Questions

1. **Component Interface**: What protocol should tdom components implement?
    - `__html__()` method?
    - `render()` method returning Node?
    - Support both?

2. **Component Syntax**: How should components be referenced in templates?
    - `<MyComponent />` (requires name resolution)
    - Direct interpolation: `{MyComponent()}`?
    - Both?

3. **Props vs Attributes**: How to distinguish component props from HTML attributes?
    - All lowercase = HTML attribute?
    - CamelCase = component prop?
    - Use different syntax?

4. **Error Handling**: How to report dependency injection errors?
    - Raise at parse time?
    - Raise at render time?
    - Collect and report multiple errors?

5. **Performance**: Impact of dependency injection on rendering performance?
    - Caching strategies?
    - Lazy resolution?
    - Profile and optimize?

## Next Steps

1. **Prototype tdom Changes**:
    - Fork tdom or work in branch
    - Implement minimal `config`/`context` support
    - Create pluggable component hooks
    - Get feedback on API design

2. **Build Basic Integration**:
    - Implement simple component locator
    - Integrate DefaultInjector
    - Create "hello world" example
    - Validate approach

3. **Expand Capabilities**:
    - Add KeywordInjector support
    - Add HopscotchInjector support
    - Create comprehensive examples
    - Document patterns

4. **Upstream to tdom**:
    - Propose minimal changes as PR
    - Keep svcs-specific code in tdom-svcs
    - Ensure no svcs dependency in core tdom
    - Maintain backward compatibility

## References

- **tdom**: Python 3.14 t-string HTML templating
- **svcs**: Service container library by Hynek Schlawack
- **svcs-di**: Automatic dependency injection layer for svcs
- **PEP 750**: Template Strings (t-strings)
- **Inject[T]**: Type marker for dependency injection

## Conclusion

The integration of tdom and svcs-di is architecturally sound and achievable through minimal, focused changes to tdom
that enable powerful dependency injection capabilities in tdom-svcs. The pluggable design ensures that core tdom remains
dependency-free while enabling advanced features like multi-implementation resolution and context-aware component
selection in the policy layer.

The three-injector hierarchy (Default → Keyword → Hopscotch) provides a clear progression from simple service injection
to advanced context-aware component resolution, making it easy for developers to adopt the complexity level they need.
