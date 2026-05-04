# Specification: Component Lifecycle Middleware System

## Goal
Implement a pluggable middleware framework that provides hooks into component initialization and rendering lifecycle phases, enabling developers to add logging, validation, transformation, and error handling capabilities without modifying core component or rendering logic.

## User Stories
- As a component developer, I want to intercept component resolution and rendering at multiple lifecycle phases so that I can add cross-cutting concerns like logging and validation
- As a framework user, I want to apply middleware globally or to specific components so that I can control which components receive middleware processing

## Specific Requirements

**Middleware Protocol Definition**
- Define `Middleware` protocol with methods for each lifecycle phase: `pre_resolution`, `post_resolution`, `before_render`, `post_render`, `on_error`, and `cleanup`
- Each phase method receives shared context (svcs.Container) and phase-specific data
- Middleware methods return phase-specific result or None to pass control to next middleware
- Protocol uses structural subtyping so implementations don't require inheritance

**Pre-Resolution Phase**
- Called before component name lookup begins
- Receives component name and context (svcs.Container)
- Can short-circuit by returning alternative component name or None to continue
- Enables conditional component routing based on context

**Post-Resolution Phase**
- Called after ComponentLookup resolves component type but before instantiation
- Receives resolved component type and context (svcs.Container)
- Can short-circuit by returning alternative component type or None to continue
- Enables component type substitution or validation

**Before-Render Phase**
- Called after Inject[] resolution but before component instantiation/execution
- Receives component target (class/function), resolved kwargs dictionary, and context
- Can modify resolved kwargs immutably by returning new kwargs dict
- Returns modified kwargs or None to use original kwargs
- Enables dependency validation and prop transformation

**Post-Render Phase**
- Called after component renders to Node but before returning to caller
- Receives rendered Node and context (svcs.Container)
- Can transform Node immutably by creating new Node instances
- Returns transformed Node or None to use original Node
- Operates on tdom Element nodes with tag, attrs, and children fields

**Error Handling Phase**
- Called when exception occurs during any lifecycle phase
- Receives exception object, phase name string, and context
- Can return fallback Node, re-raise exception, or return None to propagate
- Simple error handling without complex per-component or per-exception strategies
- Keeps error middleware straightforward for initial implementation

**Cleanup Phase**
- Executes after rendering completes (success or failure)
- Always runs like finally block to ensure cleanup even on errors
- Receives success boolean flag and context (svcs.Container)
- No return value expected (void operation)
- Use cases: releasing resources, closing connections, logging completion

**Middleware Chain Execution**
- Execute middleware in registration order (first registered runs first)
- Each middleware can pass control to next or short-circuit the chain
- Short-circuiting returns result immediately without calling remaining middleware
- Context (svcs.Container) flows through entire middleware chain
- Chain supports early termination when middleware returns non-None result

**Middleware Registration and Configuration**
- Static registration at application startup via Config object
- Config protocol gains `middleware` attribute containing ordered list of Middleware instances
- No dynamic runtime registration (keeps initialization predictable)
- Global middleware applies to all components by default
- Component-specific middleware via registration mapping in Config

**Conditional Middleware Application**
- Middleware can inspect component metadata to decide whether to process
- Support filtering by component type using isinstance checks
- Support filtering by component name using string matching
- Support filtering by context attributes from svcs.Container
- Filtering logic resides in middleware implementation, not framework

**Node Walker Utility**
- Separate utility function `walk_nodes(node, matcher, transformer)` for traversing Node trees
- Matcher function receives Node and returns boolean for whether to transform
- Transformer function receives matching Node and returns transformed Node
- Walker recursively processes Element nodes with children
- Returns new Node tree with transformations applied immutably
- Not part of middleware protocol but available for post-render middleware implementations

## Visual Design

No visual assets provided.

## Existing Code to Leverage

**Config Protocol Pattern**
- Config protocol in `processor.py` already establishes configuration pattern with `component_lookup` attribute
- Extend Config protocol to add `middleware: list[Middleware] | None` attribute
- Maintains backward compatibility by defaulting to None
- Follows existing structural subtyping approach without inheritance

**ComponentLookup Service Pattern**
- ComponentLookup in `services/component_lookup/component_lookup.py` implements service with svcs.Container
- Shows pattern for injector retrieval and component construction
- Middleware can use similar pattern to access services from container
- Demonstrates error handling with custom exceptions like ComponentNotFoundError

**Protocol-Based Design Pattern**
- Multiple protocols in codebase: ComponentLookup, Config, ComponentLookupProtocol, ComponentNameRegistryProtocol
- All use `typing.Protocol` with structural subtyping
- Runtime checkable protocols in tests using `@runtime_checkable` decorator
- Middleware protocol should follow same pattern for consistency

**html() Function Integration Point**
- `html()` function in `processor.py` already accepts config and context parameters
- Currently implements fast path when both are None
- Middleware hooks will intercept between template parsing and Node construction
- Shared context already flows through html() as svcs.Container

**Node Immutable Transformation Pattern**
- tdom Node is dataclass with `__replace__` method for immutable updates
- Element dataclass has fields: tag, attrs, children
- Post-render middleware can use `node.__replace__(children=new_children)` pattern
- Walker utility should leverage this immutability for transformations

## Out of Scope
- Built-in middleware implementations for logging, validation, or timing
- Async middleware support or async lifecycle hooks
- Dynamic middleware registration at runtime after startup
- Component decorator for attaching middleware (future @component decorator mentioned but not this spec)
- Middleware ordering controls beyond registration order
- Middleware priority or weight systems
- Middleware dependencies or inter-middleware communication beyond shared context
- Complex error handling strategies with per-component or per-exception routing
- Performance optimization for middleware chain execution
- Middleware hot-reloading or runtime reconfiguration
