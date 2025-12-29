# Task Breakdown: Component Lifecycle Middleware System

## Overview
Total Tasks: 39 sub-tasks organized into 5 major task groups

## Task List

### Protocol and Model Definitions

#### Task Group 1: Core Protocol Layer
**Dependencies:** None

- [x] 1.0 Complete protocol definitions and models
  - [x] 1.1 Write 2-8 focused tests for Middleware and Context protocols
    - Limit to 2-8 highly focused tests maximum
    - Test protocol satisfaction via isinstance() checks
    - Test structural subtyping (objects satisfy protocol without inheriting)
    - Test dict-like Context protocol with both dict and svcs.Container
    - Skip exhaustive edge case testing
  - [x] 1.2 Create middleware/models.py module structure
    - Create directory: `src/tdom_svcs/middleware/`
    - Create file: `src/tdom_svcs/middleware/models.py`
    - Create file: `src/tdom_svcs/middleware/__init__.py`
  - [x] 1.3 Define Context Protocol in models.py
    - Add `@runtime_checkable` decorator from typing
    - Define `__getitem__(self, key: str) -> Any` method
    - Define `get(self, key: str, default: Any = None) -> Any` method
    - Document dict-like retrieval interface
    - Document that svcs.Container and plain dict both satisfy this protocol
    - Reference pattern: `ComponentLookupProtocol` in `services/component_lookup/models.py`
  - [x] 1.4 Define Middleware Protocol in models.py
    - Add `@runtime_checkable` decorator from typing
    - Add `priority: int` attribute with documentation (range -100 to +100, default 0)
    - Define `__call__(self, component: type | Callable[..., Any], props: dict[str, Any], context: Context) -> dict[str, Any] | None`
    - Document that method receives component (class or function), props dict, and context
    - Document that middleware can detect type via `isinstance(component, type)` (True for classes, False for functions)
    - Document return value: modified props dict to continue, None to halt execution
    - Document structural subtyping - implementations don't need to inherit
    - Reference pattern: `ComponentLookupProtocol` in `services/component_lookup/models.py`
  - [x] 1.5 Create middleware/exceptions.py for custom exceptions
    - Create `MiddlewareExecutionHaltedError` exception class
    - Create `MiddlewareNotFoundError` exception class
    - Create `ContextNotSetupError` exception class with helpful setup_container() guidance
    - Follow error message pattern from `services/component_lookup/exceptions.py`
    - Provide actionable error messages with code examples
  - [x] 1.6 Ensure protocol layer tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify protocols work with structural subtyping
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- Context protocol satisfied by both dict and svcs.Container
- Middleware protocol accepts both class and function components
- Custom exceptions provide helpful error messages
- Full type safety with mypy and pyright

### Middleware Management Layer

#### Task Group 2: MiddlewareManager and Setup Utilities
**Dependencies:** Task Group 1

- [x] 2.0 Complete middleware management infrastructure
  - [x] 2.1 Write 2-8 focused tests for MiddlewareManager
    - Limit to 2-8 highly focused tests maximum
    - Test middleware registration and priority sorting
    - Test execution with both sync and async middleware
    - Test halt-on-None behavior with exception raising
    - Test with both function and class components
    - Skip exhaustive edge case coverage
  - [x] 2.2 Create MiddlewareManager class in middleware/manager.py
    - Create file: `src/tdom_svcs/middleware/manager.py`
    - Use dataclass with thread-safe implementation
    - Add `_middleware: list[Middleware]` field with default_factory=list
    - Add `_lock: threading.Lock` field for thread safety
    - Reference pattern: `ComponentNameRegistry` in `services/component_registry/component_name_registry.py`
  - [x] 2.3 Implement MiddlewareManager.register_middleware()
    - Signature: `register_middleware(self, middleware: Middleware) -> None`
    - Validate middleware satisfies Middleware protocol
    - Store middleware in priority-sorted list (lower priority first)
    - Use threading.Lock for thread-safe registration
    - Raise TypeError if middleware doesn't satisfy protocol
  - [x] 2.4 Implement MiddlewareManager.execute()
    - Signature: `execute(self, component: type | Callable[..., Any], props: dict[str, Any], context: Context) -> dict[str, Any]`
    - Accept both class components (type) and function components (Callable)
    - Sort middleware by priority before execution (lower numbers first)
    - Execute middleware in priority order, passing props from one to next
    - Detect async middleware via `inspect.iscoroutinefunction(middleware.__call__)`
    - Automatically await async middleware in execution chain
    - Support mixed sync and async middleware
    - Halt immediately if middleware returns None, raising middleware-defined exception
    - Each middleware receives same component reference (no component transformation)
    - Return final transformed props dict
  - [x] 2.5 Implement setup_container() utility function
    - Create in `src/tdom_svcs/middleware/__init__.py`
    - Signature: `setup_container(context: Context, registry: Any = None) -> None`
    - Accept any dict-like context (plain dict, or any Context protocol implementation)
    - When used with svcs.Registry: register via `registry.register_value(Context, context)`
    - When used with plain dict: validate protocol only
    - Document usage during app initialization before rendering
    - No hard svcs/svcs-di dependency
  - [x] 2.6 Export public API from middleware/__init__.py
    - Export Context protocol
    - Export Middleware protocol
    - Export MiddlewareManager class
    - Export setup_container function
    - Export custom exceptions
  - [x] 2.7 Ensure middleware management tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify priority-based execution works
    - Verify halt-on-None behavior works
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- MiddlewareManager handles both sync and async middleware
- Priority-based ordering works correctly (lower numbers first)
- Execution halts on None return with proper exception
- Thread-safe implementation for free-threaded Python
- setup_container() works with any dict-like context

### Component Decorator and Per-Component Middleware

#### Task Group 3: @component Decorator Implementation
**Dependencies:** Task Group 2

- [x] 3.0 Complete @component decorator and registration
  - [x] 3.1 Write 2-8 focused tests for @component decorator
    - Limit to 2-8 highly focused tests maximum
    - Test decorator with middleware dict parameter
    - Test per-component middleware storage in metadata
    - Test imperative register_component() function
    - Test compatibility with existing @injectable decorator
    - Skip exhaustive decorator combination testing
  - [x] 3.2 Create middleware/decorators.py module
    - Create file: `src/tdom_svcs/middleware/decorators.py`
    - Import necessary types and utilities
    - Plan for metadata storage on component objects
  - [x] 3.3 Implement @component decorator
    - Signature: `@component(middleware: dict[str, list[Middleware]] | None = None, **kwargs)`
    - Middleware dict maps lifecycle phases to middleware lists: `{"pre_resolution": [...], "post_resolution": [...]}`
    - Support same kwargs as @injectable (resource, location, etc.)
    - Store middleware dict in component metadata using `__tdom_svcs_middleware__` attribute
    - Register component in ComponentNameRegistry
    - Reference pattern: Existing @injectable decorator from svcs-di
    - Maintain compatibility with @injectable decorated components
  - [x] 3.4 Implement register_component() imperative function
    - Signature: `register_component(component: type | Callable, middleware: dict[str, list[Middleware]] | None = None, **kwargs)`
    - Provide non-decorator alternative for component registration
    - Store same metadata as decorator approach
    - Support both class and function components
    - Register in ComponentNameRegistry like decorator does
  - [x] 3.5 Create per-component middleware retrieval utility
    - Function to retrieve middleware from component metadata
    - Signature: `get_component_middleware(component: type | Callable) -> dict[str, list[Middleware]]`
    - Return empty dict if no middleware registered
    - Handle both decorator and imperative registration
  - [x] 3.6 Export decorator API from middleware/__init__.py
    - Export @component decorator
    - Export register_component function
    - Export get_component_middleware utility
  - [x] 3.7 Ensure decorator tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify metadata storage works
    - Verify compatibility with @injectable
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- @component decorator stores middleware in metadata
- register_component() provides imperative alternative
- Decorator works with both class and function components
- Compatible with existing @injectable decorator
- Metadata retrieval utility works correctly

### Hook System Integration

#### Task Group 4: Integration with Existing Hook System
**Dependencies:** Task Groups 1-3, Roadmap Item 1 (Core tdom Hooks)

- [x] 4.0 Complete middleware integration with hook system
  - [x] 4.1 Write 2-8 focused tests for hook integration
    - Limit to 2-8 highly focused tests maximum
    - Test middleware execution before component resolution
    - Test global middleware execution
    - Test per-component middleware execution after global middleware
    - Test with both class and function components
    - Skip exhaustive integration scenarios
  - [x] 4.2 Add middleware execution to pre-resolution hook
    - Integrate MiddlewareManager.execute() before component resolution
    - For class components: pass component type to execute()
    - For function components: pass function reference to execute()
    - Use runtime detection: `isinstance(component, type)` to branch
    - Execute global middleware from MiddlewareManager
    - Execute per-component middleware after global middleware
    - Both respect priority ordering
  - [x] 4.3 Add middleware execution to post-resolution hook
    - Execute middleware after component resolution but before invocation
    - Pass resolved component and props to middleware
    - Use returned props for component invocation
    - Handle both sync and async component paths
  - [x] 4.4 Add middleware execution to rendering hook
    - Execute middleware during rendering phase
    - Transform rendering output through middleware chain
    - Maintain async support in rendering path
  - [x] 4.5 Update processor.py to support middleware flow
    - Add middleware parameter to html() wrapper if needed
    - Pass middleware context through resolution flow
    - Ensure middleware execution doesn't modify tdom core
    - Keep all middleware logic in tdom-svcs layer only
  - [x] 4.6 Ensure hook integration tests pass
    - Run ONLY the 2-8 tests written in 4.1
    - Verify middleware executes at correct lifecycle points
    - Verify global + per-component ordering works
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 4.1 pass
- Middleware wraps pre-resolution, post-resolution, and rendering hooks
- Global middleware executes before per-component middleware
- Priority ordering maintained across both global and per-component middleware
- Works with both class and function components
- Middleware integrated without modifying tdom core
- Async middleware works in async component paths

### Examples and Documentation

#### Task Group 5: Example Implementations and Usage Patterns
**Dependencies:** Task Groups 1-4

- [x] 5.0 Complete example implementations
  - [x] 5.1 Create examples/middleware/ directory structure (ALREADY EXISTS - verified)
    - Directory exists: `examples/middleware/`
    - Contains existing examples: 01-04 and README.md
    - Plan: add examples 05-07 for error handling, global+per-component, and async
  - [x] 5.2 Implement LoggingMiddleware example
    - EXISTS in `examples/middleware/01_basic_middleware.py`
    - Shows timing and component name logging
    - Demonstrates priority usage (-10 for early execution)
    - Works with both function and class components
    - Shows two usage patterns: with svcs-di and without (plain dict)
  - [x] 5.3 Implement ValidationMiddleware example
    - EXISTS in `examples/middleware/01_basic_middleware.py`
    - Shows props validation with type checking
    - Demonstrates halt-on-error by returning None
    - Demonstrates priority usage (0 for default execution)
    - Works with both function and class components
  - [x] 5.4 Implement TransformationMiddleware example
    - EXISTS in `examples/middleware/01_basic_middleware.py`
    - Shows props transformation patterns
    - Demonstrates priority usage (10 for late execution)
    - Shows modifying props for both function and class components
    - Returns modified props dict
  - [x] 5.5 Implement ErrorHandlingMiddleware example
    - Created `examples/middleware/05_error_handling_middleware.py`
    - Shows exception catching and handling patterns
    - Demonstrates wrapping middleware execution
    - Shows fallback rendering on error
    - Demonstrates circuit breaker pattern
    - Shows priority-based error handling (early detection, late recovery)
  - [x] 5.6 Create comprehensive usage example
    - Created `examples/middleware/06_global_and_per_component.py`
    - Demonstrates setup_container() usage
    - Shows global middleware registration via MiddlewareManager
    - Shows per-component middleware via @component decorator
    - Shows imperative register_component() as alternative
    - Demonstrates execution order: global (-10, 0, 10) then per-component
    - Shows stateless middleware (via MiddlewareManager) vs stateful (via context)
    - Includes both class components (Button, Card) and function components (Heading, Paragraph)
    - Includes comprehensive inline documentation
  - [x] 5.7 Create async middleware example
    - Created `examples/middleware/07_async_middleware.py`
    - Shows async middleware implementation with async __call__
    - Demonstrates mixed sync/async middleware chain
    - Shows automatic async detection and awaiting
    - Demonstrates async component rendering with middleware
    - Shows real-world async use cases (database, API, validation, error handling)
    - Uses await manager.execute_async()
  - [x] 5.8 Add inline documentation to examples
    - All examples have detailed docstrings explaining purpose
    - Inline comments for complex middleware logic
    - Priority system usage documented in all examples
    - Stateless vs stateful middleware patterns documented in 06_global_and_per_component.py
    - svcs-di vs plain dict patterns documented throughout examples
    - README.md updated with comprehensive documentation for all 7 examples

**Acceptance Criteria:**
- [x] All example files created in examples/middleware/
- [x] Examples demonstrate both function and class component support
- [x] Examples show priority-based execution ordering
- [x] Examples demonstrate both usage patterns (with/without svcs-di)
- [x] Examples show global + per-component middleware execution order
- [x] Examples demonstrate async middleware support
- [x] Examples include comprehensive inline documentation
- [x] No built-in middleware implementations in src/ (examples only)

### Final Integration Testing

#### Task Group 6: Integration Testing and Gap Analysis
**Dependencies:** Task Groups 1-5

- [x] 6.0 Review existing tests and fill critical gaps only
  - [x] 6.1 Review tests from Task Groups 1-5
    - Review the 2-8 tests written for protocols (Task 1.1): 10 tests found
    - Review the 2-8 tests written for MiddlewareManager (Task 2.1): 13 tests found
    - Review the 2-8 tests written for @component decorator (Task 3.1): 8 tests found
    - Review the 2-8 tests written for hook integration (Task 4.1): 7 tests found
    - Review setup_container tests: 12 tests found
    - Review protocol tests: 8 tests found
    - Total existing tests: 57 tests (exceeding initial estimate)
  - [x] 6.2 Analyze test coverage gaps for THIS feature only
    - Identified critical middleware workflows lacking test coverage
    - Focused ONLY on gaps related to middleware system requirements
    - Did NOT assess entire application test coverage
    - Prioritized end-to-end middleware execution workflows
    - Checked integration between global and per-component middleware
    - Checked async/sync mixed middleware chains
    - Checked halt-on-error propagation
    - **Critical gaps identified:**
      1. End-to-end integration test with setup_container() -> register -> execute -> hooks
      2. Mixed sync/async middleware chains (comprehensive test)
      3. Error propagation from middleware
      4. Stateful vs stateless middleware together
      5. Thread-safe concurrent middleware execution
      6. Multiple components with different middleware
      7. Middleware halt behavior in integration scenario
      8. Lifecycle phase transitions (pre -> post -> rendering)
      9. Context service injection in middleware
      10. Performance stress test with many middleware
  - [x] 6.3 Write up to 10 additional strategic tests maximum
    - Added exactly 10 new tests to fill identified critical gaps
    - Focused on integration points between components
    - Tested end-to-end: setup_container() -> register -> execute -> integrate with hooks
    - Tested global + per-component middleware execution order
    - Tested middleware with both class and function components
    - Tested mixed sync/async middleware chains
    - Tested error propagation and halt behavior
    - Did NOT write comprehensive coverage for all scenarios
    - Skipped edge cases unless business-critical
    - **New tests created in `tests/middleware/test_integration_end_to_end.py`:**
      1. test_end_to_end_workflow_with_setup_and_execution
      2. test_mixed_sync_async_middleware_chain
      3. test_error_propagation_from_middleware
      4. test_stateful_and_stateless_middleware_together
      5. test_thread_safe_concurrent_middleware_execution
      6. test_multiple_components_with_different_middleware
      7. test_middleware_halt_behavior_in_integration
      8. test_lifecycle_phase_transitions
      9. test_middleware_with_context_service_injection
      10. test_performance_stress_with_many_middleware
  - [x] 6.4 Run feature-specific tests only
    - Ran ONLY tests related to middleware system feature
    - Total tests: 67 tests (57 existing + 10 new)
    - Did NOT run the entire application test suite
    - Verified critical middleware workflows pass: ALL PASSED
    - Verified type checking passes with ty check: PASSED for new integration tests
    - Verified thread safety in free-threaded Python environment: TESTED via test_thread_safe_concurrent_middleware_execution
    - Verified async middleware execution: TESTED via test_mixed_sync_async_middleware_chain

**Acceptance Criteria:**
- [x] All feature-specific tests pass (67 tests total: 57 existing + 10 new)
- [x] Critical middleware workflows are covered
- [x] Exactly 10 additional tests added (no more than maximum)
- [x] Testing focused exclusively on middleware system requirements
- [x] Type checking passes with ty check for new integration tests
- [x] Thread-safe implementation verified via concurrent execution test
- [x] Async middleware execution verified via mixed chain test
- [x] Integration with hooks verified via end-to-end test

## Execution Order

Recommended implementation sequence:
1. Protocol and Model Definitions (Task Group 1) - Foundation for all middleware components
2. Middleware Management Layer (Task Group 2) - Core manager and setup utilities
3. Component Decorator and Per-Component Middleware (Task Group 3) - Per-component lifecycle support
4. Hook System Integration (Task Group 4) - Integration with existing tdom-svcs hooks
5. Examples and Documentation (Task Group 5) - Usage demonstrations
6. Final Integration Testing (Task Group 6) - End-to-end verification and gap filling

## Key Dependencies

- **External**: Roadmap Item 1 (Minimal tdom Core Hooks) must be completed before Task Group 4
- **Task Group 2** depends on Task Group 1 (protocols and models)
- **Task Group 3** depends on Task Group 2 (MiddlewareManager)
- **Task Group 4** depends on Task Groups 1-3 and Roadmap Item 1
- **Task Group 5** depends on Task Groups 1-4 (all core functionality)
- **Task Group 6** depends on Task Groups 1-5 (all implementation complete)

## Testing Strategy

- Each task group (1-5) writes 2-8 highly focused tests at the start of implementation
- Tests verify critical behaviors only, not exhaustive coverage
- Each task group runs ONLY its own tests, not the entire suite
- Task Group 6 adds maximum 10 tests to fill critical integration gaps
- Total expected tests: approximately 18-42 tests for entire feature
- **ACTUAL: 67 tests (57 existing + 10 new integration tests)**
- Focus on end-to-end workflows and integration points
- Verify type safety with mypy and pyright
- Verify thread safety for free-threaded Python

## Reusable Patterns

- **Protocol definitions**: Follow `ComponentLookupProtocol` pattern from `services/component_lookup/models.py`
- **Service implementation**: Follow `ComponentNameRegistry` pattern from `services/component_registry/component_name_registry.py`
- **Exception handling**: Follow patterns from `services/component_lookup/exceptions.py`
- **Thread safety**: Use threading.Lock like `ComponentNameRegistry`
- **Decorator pattern**: Reference existing @injectable decorator from svcs-di
- **Test structure**: Follow test patterns from `tests/test_component_name_registry.py`

## Out of Scope

- Built-in middleware implementations in src/ (only examples in examples/)
- Standard error result types (middleware defines their own exceptions)
- Middleware composition/chaining helper utilities beyond basic execution order
- Middleware performance profiling tools
- Conditional middleware activation based on component properties (other than per-component registration)
- Per-request context lifecycle (context is container lifecycle only)
- Middleware configuration via config files or environment variables
- Requiring svcs/svcs-di as hard dependencies (middleware uses dict-like interfaces)
- Middleware state persistence across requests
- Complex middleware dependencies or ordering constraints beyond priority numbers
