# Specification: Component Lifecycle Middleware System

## Goal

Create a pluggable middleware system that wraps tdom-svcs hooks for logging, validation, transformation, and error
handling during component initialization and rendering, using priority-based execution with dict-like interfaces that
work with or without svcs/svcs-di.

## User Stories

- As a developer, I want to add logging middleware to track component rendering performance for both function and class
  components without modifying component code
- As a developer, I want to validate props before rendering using middleware that works with both functions and classes
  and can halt execution on validation failure
- As a developer, I want to register per-component middleware using the @component decorator to apply specific middleware
  to individual components while maintaining global middleware for all components

## Specific Requirements

**Define Middleware Protocol**

- Create `Middleware` Protocol in `src/tdom_svcs/middleware/models.py` with `@runtime_checkable` decorator
- Protocol has `priority: int` attribute (range -100 to +100, default 0, lower executes first)
- Protocol has `__call__(self, component: type | Callable[..., Any], props: dict[str, Any], context: Context) -> dict[str, Any] | None`
  method
- Method receives component (class or function), its props dict, and injectable context
- Middleware can detect type via `isinstance(component, type)` - True for classes, False for functions
- Method returns modified props dict to continue execution, or None to halt
- Use structural subtyping - implementations don't need to inherit
- Single protocol works for both function and class components (not separate protocols)

**Define Context Protocol for middleware injection**

- Create `Context` Protocol in `src/tdom_svcs/middleware/models.py` with `@runtime_checkable` decorator
- Protocol defines dict-like retrieval interface: `__getitem__(self, key: str) -> Any`
- Protocol defines `get(self, key: str, default: Any = None) -> Any` method
- Works with any dict-like object - not tied to svcs/svcs-di
- `svcs.Container` naturally satisfies this protocol (as one implementation option)
- Plain Python dict also satisfies the protocol (for non-svcs usage)
- Middleware retrieves dependencies via `context[key]` or `context.get(key, default)`
- Keep minimal - only define retrieval methods, no svcs-specific assumptions

**Create setup_container() utility function**

- Implement standalone function in `src/tdom_svcs/middleware/__init__.py`
- Signature: `setup_container(context: Context) -> None` (accepts any dict-like context)
- Works with svcs.Container, plain dict, or any object satisfying Context protocol
- Registers context object to make it available to middleware
- When used with svcs.Container, registers via `container.register_value(Context, context)`
- When used with plain dict, simply stores reference for middleware access
- Called during app initialization before rendering
- No svcs/svcs-di dependency - works with any dict-like context

**Implement MiddlewareManager for stateless middleware**

- Create `MiddlewareManager` class in `src/tdom_svcs/middleware/manager.py`
- Manages collection of stateless middleware registered at startup
- Method `register_middleware(middleware: Middleware) -> None` for registration
- Method `execute(component: type | Callable[..., Any], props: dict[str, Any], context: Context) -> dict[str, Any]` for execution
- Accepts both class components (type) and function components (Callable)
- Sorts middleware by priority (lower numbers first) before execution
- Executes middleware in priority order, passing props from one to next
- Each middleware receives the same component reference (no transformation of component, only props)
- Halts execution immediately if any middleware returns None
- Raises middleware-defined exception when middleware returns None
- Stores middleware in priority-sorted list for efficient execution

**Support stateful middleware via context**

- Stateful middleware (like static asset collectors) stored in context dict
- When using svcs.Container: register via `container.register_factory()` or `container.register_value()`
- When using plain dict: store middleware instances directly in dict
- Middleware retrieved from context via dict-like access: `context['asset_collector']`
- Stateful middleware participates in context lifecycle (container-level, not per-request)
- MiddlewareManager only handles stateless middleware from registry
- Distinction: stateless via `MiddlewareManager.register_middleware()`, stateful via context dict

**Integrate middleware with existing hook system**

- Wrap pre-resolution, post-resolution, and rendering hooks from roadmap item 1
- Add middleware execution before component resolution in the processor flow
- For class components: pass component type to MiddlewareManager.execute()
- For function components: pass function reference to MiddlewareManager.execute()
- Runtime detection via `isinstance(component, type)` to branch between class and function paths
- Use returned props dict for subsequent component resolution/invocation
- Middleware hooks into the existing processor flow without modifying tdom core
- Middleware execution happens in tdom-svcs layer only

**Support async middleware execution**

- Detect if middleware `__call__` is async via `inspect.iscoroutinefunction()`
- Automatically await async middleware in execution chain
- Support mixed sync and async middleware in same execution chain
- Maintain priority-based ordering regardless of sync/async
- Halt execution on failure applies to both sync and async middleware

**Type-safe handling of functions and classes**

- Use Union type `type | Callable[..., Any]` throughout middleware signatures
- Middleware implementations can branch on `isinstance(component, type)` for different handling
- Type checker understands both branches via type narrowing
- For class components: `isinstance(component, type)` is True, component is `type`
- For function components: `isinstance(component, type)` is False, component is `Callable[..., Any]`
- MiddlewareManager.execute() accepts both types with single method signature
- No separate code paths needed at manager level - branching happens in middleware implementations
- Test both function and class components with same middleware

**Create @component decorator for per-component middleware**

- Implement `@component` decorator in `src/tdom_svcs/middleware/decorators.py`
- Similar to `@injectable` but adds middleware lifecycle support
- Signature: `@component(middleware: dict[str, list[Middleware]] | None = None, **kwargs)`
- Middleware dict maps lifecycle phases to middleware lists: `{"pre_resolution": [...], "post_resolution": [...]}`
- Decorator supports same kwargs as `@injectable` (resource, location, etc.)
- Registers component in both ComponentNameRegistry and with per-component middleware
- Provide imperative function: `register_component(component, middleware=None, **kwargs)`
- Imperative function for registration without decorator syntax
- Both decorator and function store middleware in component metadata
- Per-component middleware executes after global middleware (both respect priority ordering)

**Example middleware implementations**

- Provide example LoggingMiddleware showing timing and component names (works with both functions and classes)
- Provide example ValidationMiddleware showing props validation with halt-on-error
- Provide example TransformationMiddleware showing props transformation
- Provide example ErrorHandlingMiddleware showing exception catching patterns
- Examples demonstrate priority usage (e.g., logging at -10, validation at 0, transformation at 10)
- Show two usage patterns: with svcs-di (`Inject[T]`) and without (plain dict access)
- Examples demonstrate middleware works with any dict-like context (not just svcs.Container)
- Show middleware detecting component type: `isinstance(component, type)` for class vs function
- Demonstrate middleware modifying props for both function and class components
- Show `@component` decorator usage with per-component middleware registration
- Show imperative `register_component()` function as alternative to decorator
- Demonstrate global middleware + per-component middleware execution order
- Examples are in `examples/middleware/` directory, not in src (not built-in implementations)

## Visual Design

No visual assets provided.

## Existing Code to Leverage

**ComponentLookup Protocol pattern (processor.py lines 16-57)**

- Use same `@runtime_checkable` Protocol decorator approach
- Follow structural subtyping pattern without requiring inheritance
- Apply similar docstring documentation style
- Place Middleware Protocol in similar location structure

**ComponentNameRegistry service patterns (component_registry/)**

- Use similar registration and retrieval patterns for MiddlewareManager
- Follow same error handling approach with custom exceptions
- Apply same dataclass patterns for stateless service implementations
- Reference for organizing middleware module structure

**Protocol definitions in models.py files**

- Follow existing pattern of Protocol definitions in separate models.py files
- Use `@runtime_checkable` decorator consistently
- Keep Protocol definitions minimal and focused
- Apply same documentation standards

**Test patterns from test_component_lookup.py**

- Follow same test structure for middleware tests
- Use dataclass fixtures for test middleware implementations
- Apply same error testing patterns with pytest.raises
- Test protocol satisfaction via `isinstance()` checks

**Existing exception patterns (component_lookup/exceptions.py)**

- Create similar middleware-specific exceptions in `middleware/exceptions.py`
- Provide helpful error messages mentioning setup_container() and registration
- Include guidance on how to fix configuration issues
- Use same exception hierarchy patterns

**ComponentLookup async detection pattern (component_lookup.py lines 89-94)**

- Reference async detection via `isinstance(component, type)` and checking `__call__` method
- Similar pattern needed for middleware: detect component type with `isinstance(component, type)`
- Use same `inspect` module utilities for runtime type checking
- Apply same branching approach for handling different component types

**Existing @injectable decorator pattern (svcs-di)**

- Use @injectable as reference for @component decorator implementation
- Follow same decorator signature patterns with optional kwargs
- Apply same metadata storage approach for decorator parameters
- Reference scan_components() pattern for discovering @component decorated items
- Store middleware dict in component metadata similar to resource/location metadata
- Maintain compatibility with existing @injectable decorated components

## Out of Scope

- Built-in middleware implementations in src (only examples in examples/)
- Standard error result types (middleware defines their own exceptions)
- Middleware composition/chaining helper utilities beyond basic execution order
- Middleware performance profiling tools
- Conditional middleware activation based on component properties (other than per-component registration)
- Per-request context lifecycle (context is container lifecycle only)
- Middleware configuration via config files or environment variables
- Requiring svcs/svcs-di as hard dependencies (middleware uses dict-like interfaces)
- Middleware state persistence across requests
- Complex middleware dependencies or ordering constraints beyond priority numbers
