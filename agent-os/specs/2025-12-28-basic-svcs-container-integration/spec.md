# Specification: Basic svcs Container Integration

## Goal
Create an adapter layer that implements the ComponentLookup protocol to bridge tdom's component system with svcs container, enabling dependency injection for components through a component name registry and injector-based resolution for both sync and async components.

## User Stories
- As a tdom-svcs developer, I want to register component classes with string names so that tdom templates can resolve them via dependency injection
- As a tdom-svcs user, I want to call a setup function to initialize the container with necessary services so that component resolution works out of the box

## Specific Requirements

**Implement ComponentLookup Protocol in tdom-svcs**
- Create class that implements ComponentLookup protocol from Item 1 (tdom_svcs.processor)
- Accept svcs.Container in __init__ method
- Implement __call__(name: str, context: Mapping[str, Any]) -> Callable | None
- Look up component type from ComponentNameRegistry using string name
- Retrieve injector from container (minimum KeywordInjector)
- Use injector to construct component instance
- Return constructed callable component or None if name not found
- Support both sync and async component construction

**Create ComponentNameRegistry Service**
- Implement service that maps component string names to type objects
- Store mapping as dict[str, type] for simple resolution
- Provide method to register name-to-type mappings
- Provide method to retrieve type by name (returns None if not found)
- Provide method to get all registered names for error suggestions
- Thread-safe for concurrent access in free-threaded Python

**Implement setup_container Helper Function**
- Create function signature: setup_container(container: svcs.Container) -> None
- Register ComponentNameRegistry as singleton service in container
- Register ComponentLookup implementation in container
- Users must explicitly call this function during application initialization
- Do NOT auto-register on package import (explicit setup only)

**Implement register_component Helper Function**
- Create function signature: register_component(registry: svcs.Registry, container: svcs.Container, name: str, component_type: type)
- Register component type in ComponentNameRegistry under string name
- Register component factory in svcs.Registry using injector pattern
- Support both dataclass components and function components
- Validate that component_type is callable or dataclass
- Raise clear errors for invalid component types

**Error Handling with Suggestions**
- Raise ComponentNotFoundError when component name lookup fails
- Include list of similar registered component names in error message
- Use fuzzy matching (difflib) to suggest close matches
- Raise InjectorNotFoundError when injector not registered in container
- Guide users to register KeywordInjector or call setup_container()
- Raise RegistryNotSetupError when ComponentNameRegistry not in container
- Include suggestion to call setup_container() in error message

**Support Both Sync and Async Components**
- Detect if component type is async function using inspect.iscoroutinefunction
- Use KeywordInjector for sync components
- Use KeywordAsyncInjector for async components if available
- Handle async component construction with await
- Raise clear errors if async component used without AsyncInjector registered

**Integration with tdom Hooks from Item 1**
- ComponentLookup receives component name as string from tdom
- Extract name from interpolation using callable.__name__
- Context parameter passed through but not used in basic integration
- Look up type from ComponentNameRegistry
- Construct using injector with three-tier precedence (kwargs, container, defaults)
- Return constructed component or None for fallback behavior

**Type Safety and Protocols**
- Full type hints for all public APIs
- ComponentLookup satisfies protocol through structural typing (no inheritance)
- ComponentNameRegistry uses dict[str, type] for type-safe storage
- Use typing.Any for flexible container typing
- Support runtime protocol checking with isinstance

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**ComponentLookup Protocol from Item 1 (tdom_svcs/processor.py lines 16-57)**
- Use as contract for ComponentLookup implementation
- Protocol defines __init__(container: Any) and __call__(name: str, context: Mapping[str, Any]) -> Callable | None
- Implement using structural subtyping (no inheritance needed)
- Follow mock implementation pattern from manual_verification.py (lines 44-62)
- Use @runtime_checkable for isinstance validation

**KeywordInjector Pattern (svcs-di/injectors/keyword.py lines 23-113)**
- Import KeywordInjector and KeywordAsyncInjector for component construction
- Use three-tier precedence: kwargs override, container resolution, default values
- Call injector(component_type, **props) to construct component instances
- Leverage _validate_kwargs for parameter validation
- Use get_field_infos() for analyzing component signatures

**DefaultInjector Retrieval Pattern (svcs-di/auto.py lines 452-462)**
- Use container.get(KeywordInjector) with try/except fallback
- Construct KeywordInjector(container=container) if not registered
- Apply same pattern for KeywordAsyncInjector in async path
- Handle svcs.exceptions.ServiceNotFoundError gracefully

**FieldInfo Extraction (svcs-di/auto.py lines 231-353)**
- Import get_field_infos() to analyze component signatures
- Use for validation and introspection of component parameters
- Handle both dataclass fields and function parameters
- Leverage for error messages showing expected parameters

**Mock ComponentLookup Pattern (manual_verification.py lines 44-62)**
- Use as template for ComponentLookup implementation structure
- Store container in dataclass field
- Implement __call__ with name and context parameters
- Return component from registry or None for fallback
- Print debug information during development/testing

## Out of Scope
- Decorator-based component registration (@component) - deferred to Item 3
- Package scanning and auto-discovery - deferred to Item 3
- Keyword override support in props - deferred to Item 5
- Resource-based component resolution - deferred to Item 6
- Location-based component resolution - deferred to Item 7
- Multi-implementation resolution with precedence - deferred to Items 6-7
- Middleware hooks or lifecycle events - deferred to Item 9
- Testing utilities or mock injection helpers - deferred to Item 8
- Custom injector implementations beyond using KeywordInjector
- Automatic registration on package import (must be explicit)
