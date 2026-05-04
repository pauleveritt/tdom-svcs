# Task Breakdown: Basic svcs Container Integration

## Overview
Total Tasks: 4 Task Groups
Feature Size: Small (S)

This implementation creates the foundational adapter layer that bridges tdom's component system with svcs container, enabling dependency injection for components through a component name registry and injector-based resolution.

## Task List

### Core Services Layer

#### Task Group 1: Component Name Registry Service
**Dependencies:** None

- [x] 1.0 Complete ComponentNameRegistry service
  - [x] 1.1 Write 2-8 focused tests for ComponentNameRegistry
    - Limit to 2-8 highly focused tests maximum
    - Test only critical registry behaviors (e.g., register name-to-type mapping, retrieve type by name, return None for unknown name, get all names for suggestions)
    - Skip exhaustive edge case testing
    - Test thread safety for concurrent access in free-threaded Python
  - [x] 1.2 Create ComponentNameRegistry class
    - Storage: `dict[str, type]` for name-to-type mapping
    - Method: `register(name: str, component_type: type) -> None`
    - Method: `get_type(name: str) -> type | None` (returns None if not found)
    - Method: `get_all_names() -> list[str]` (for error suggestions)
    - Thread-safe implementation for concurrent access
    - Full type hints on all methods
  - [x] 1.3 Ensure ComponentNameRegistry tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify name registration and retrieval work
    - Verify thread safety for concurrent access
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- Registry correctly stores and retrieves name-to-type mappings
- Returns None for unregistered names
- Provides all registered names for error suggestions
- Thread-safe for concurrent access

**Reference Code:**
- ServiceLocator pattern from `svcs-di/injectors/locator.py` for registry structure
- Mock ComponentLookup from Item 1 `manual_verification.py` lines 44-62

---

### Component Lookup Layer

#### Task Group 2: ComponentLookup Protocol Implementation
**Dependencies:** Task Group 1 - COMPLETED ✓

- [x] 2.0 Complete ComponentLookup implementation
  - [x] 2.1 Write 2-8 focused tests for ComponentLookup
    - Limit to 2-8 highly focused tests maximum
    - Test only critical lookup behaviors (e.g., resolve sync component by name, resolve async component by name, return None for unknown name, raise error when injector not found, raise error when registry not setup)
    - Skip exhaustive testing of all error scenarios
    - Test both sync and async component construction
  - [x] 2.2 Create ComponentLookup class implementing protocol
    - Implement protocol from Item 1 `tdom_svcs/processor.py` lines 16-57
    - `__init__(self, container: Any) -> None` - store container
    - `__call__(self, name: str, context: Mapping[str, Any]) -> Callable | None`
    - Use structural typing (no inheritance required)
    - Add `@runtime_checkable` decorator for isinstance validation
    - Full type hints on all methods
  - [x] 2.3 Implement component resolution logic
    - Retrieve ComponentNameRegistry from container
    - Raise RegistryNotSetupError if registry not found (suggest calling setup_container())
    - Look up component type using `registry.get_type(name)`
    - If type not found, raise ComponentNotFoundError with suggestions (use difflib for fuzzy matching against registry.get_all_names())
    - Return constructed component or None
  - [x] 2.4 Implement injector retrieval and component construction
    - Detect if component is async using `inspect.iscoroutinefunction()`
    - For sync components:
      - Retrieve KeywordInjector from container
      - If not found, raise InjectorNotFoundError (suggest registering KeywordInjector or calling setup_container())
      - Construct component: `injector(component_type)`
    - For async components:
      - Retrieve KeywordAsyncInjector from container
      - If not found, raise InjectorNotFoundError with async-specific guidance
      - Construct component: `await injector(component_type)`
    - Follow pattern from `svcs-di/auto.py` lines 452-462 for injector retrieval
  - [x] 2.5 Create custom exception classes
    - ComponentNotFoundError: include component name and similar name suggestions
    - InjectorNotFoundError: include guidance to register injector or call setup_container()
    - RegistryNotSetupError: include guidance to call setup_container()
    - All exceptions with clear, actionable messages
  - [x] 2.6 Ensure ComponentLookup tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify sync and async component resolution work
    - Verify error handling with helpful messages
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- ComponentLookup satisfies protocol through structural typing
- Successfully resolves both sync and async components
- Returns None for unregistered component names (after raising error)
- Clear error messages with actionable suggestions
- Proper injector retrieval with fallback error handling

**Reference Code:**
- ComponentLookup protocol from Item 1 `tdom_svcs/processor.py` lines 16-57
- Mock implementation from Item 1 `manual_verification.py` lines 44-62
- KeywordInjector pattern from `svcs-di/injectors/keyword.py` lines 23-113
- DefaultInjector retrieval from `svcs-di/auto.py` lines 452-462
- FieldInfo extraction from `svcs-di/auto.py` lines 231-353

---

### Container Initialization Layer

#### Task Group 3: Container Setup and Registration Helpers
**Dependencies:** Task Groups 1, 2

- [ ] 3.0 Complete container initialization helpers
  - [ ] 3.1 Write 2-8 focused tests for setup and registration helpers
    - Limit to 2-8 highly focused tests maximum
    - Test only critical setup behaviors (e.g., setup_container registers required services, register_component adds name-to-type mapping, register_component adds factory to registry, validates component_type is callable/dataclass)
    - Skip exhaustive validation testing
    - Test integration between setup and registration
  - [ ] 3.2 Implement setup_container helper function
    - Signature: `setup_container(container: svcs.Container) -> None`
    - Register ComponentNameRegistry as singleton in container
    - Register ComponentLookup implementation in container
    - Do NOT auto-call on import (explicit setup only)
    - Full type hints
  - [ ] 3.3 Implement register_component helper function
    - Signature: `register_component(registry: svcs.Registry, container: svcs.Container, name: str, component_type: type) -> None`
    - Validate component_type is callable or dataclass
    - Raise clear error for invalid component types
    - Register name→type mapping in ComponentNameRegistry
    - Register component factory in svcs.Registry using injector pattern
    - Support both dataclass components and function components
    - Use KeywordInjector for factory registration
    - Full type hints
  - [ ] 3.4 Ensure container setup tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify setup_container registers all required services
    - Verify register_component works for both dataclass and function components
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- setup_container successfully registers ComponentNameRegistry and ComponentLookup
- register_component validates and registers components correctly
- Component factories use KeywordInjector pattern
- Support both sync and async component registration
- Clear validation errors for invalid component types

**Reference Code:**
- Factory registration pattern from `svcs-di/auto.py`
- KeywordInjector usage from `svcs-di/injectors/keyword.py`
- FieldInfo validation from `svcs-di/auto.py` lines 231-353

---

### Integration Testing & Documentation

#### Task Group 4: End-to-End Integration Testing
**Dependencies:** Task Groups 1-3

- [ ] 4.0 Complete integration testing and verification
  - [ ] 4.1 Review tests from Task Groups 1-3
    - Review the 2-8 tests written by core-services-engineer (Task 1.1)
    - Review the 2-8 tests written by component-lookup-engineer (Task 2.1)
    - Review the 2-8 tests written by container-setup-engineer (Task 3.1)
    - Total existing tests: approximately 6-24 tests
  - [ ] 4.2 Analyze test coverage gaps for THIS feature only
    - Identify critical integration workflows lacking coverage
    - Focus ONLY on gaps related to this spec's adapter layer requirements
    - Prioritize end-to-end workflows: setup → registration → lookup → component construction
    - Do NOT assess entire application test coverage
  - [ ] 4.3 Write up to 10 additional strategic integration tests maximum
    - Add maximum of 10 new tests to fill identified critical gaps
    - Focus on end-to-end workflows:
      - Complete flow: setup_container → register_component → ComponentLookup resolves component
      - Sync component with dependencies from container
      - Async component with dependencies from container
      - Error path: component not found with helpful suggestions
      - Error path: injector not registered with helpful error
      - Error path: registry not setup with helpful error
    - Test integration with tdom hooks from Item 1 (if manual verification available)
    - Do NOT write comprehensive coverage for all edge cases
    - Skip performance tests and detailed error message formatting tests
  - [ ] 4.4 Run feature-specific tests only
    - Run ONLY tests related to this spec's adapter layer (tests from 1.1, 2.1, 3.1, and 4.3)
    - Expected total: approximately 16-34 tests maximum
    - Do NOT run the entire application test suite
    - Verify all critical adapter layer workflows pass
  - [ ] 4.5 Create integration verification script
    - Create manual verification script similar to Item 1's `manual_verification.py`
    - Demonstrate complete workflow:
      1. Create svcs.Container and svcs.Registry
      2. Call setup_container(container)
      3. Register sample components with register_component()
      4. Use ComponentLookup to resolve components by name
      5. Verify sync and async component construction
      6. Show error messages for missing components
    - Include print statements showing each step
    - Can be run manually to verify integration

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 16-34 tests total)
- Critical integration workflows for adapter layer are covered
- No more than 10 additional tests added when filling in testing gaps
- Manual verification script demonstrates complete setup → resolution workflow
- Clear documentation of how to use setup_container and register_component
- Error messages include helpful suggestions verified through testing

**Reference Code:**
- Item 1 `manual_verification.py` for verification script pattern
- Integration test patterns from svcs-di test suite
- ComponentLookup protocol usage from Item 1

---

## Execution Order

Recommended implementation sequence:
1. **Core Services Layer** (Task Group 1) - ComponentNameRegistry service ✓ COMPLETED
2. **Component Lookup Layer** (Task Group 2) - ComponentLookup protocol implementation ✓ COMPLETED
3. **Container Initialization Layer** (Task Group 3) - setup_container and register_component helpers
4. **Integration Testing & Documentation** (Task Group 4) - End-to-end verification

## Implementation Notes

**Key Integration Points:**
- ComponentLookup protocol from Item 1 (`tdom_svcs/processor.py` lines 16-57)
- KeywordInjector and KeywordAsyncInjector from svcs-di
- tdom's hook system passes component name as string to ComponentLookup.__call__()
- Context parameter available but not used in basic integration

**Critical Design Decisions:**
- Use structural typing for ComponentLookup (no inheritance required)
- ComponentNameRegistry as a service in the container (not a global registry)
- Helper function pattern for registration (decorator deferred to Item 3)
- Minimum KeywordInjector dependency for component props support
- Explicit setup via setup_container() (no auto-registration on import)

**Error Handling Strategy:**
- All errors include actionable guidance
- ComponentNotFoundError suggests similar names using difflib fuzzy matching
- InjectorNotFoundError guides user to register injector or call setup_container()
- RegistryNotSetupError indicates setup_container() not called

**Type Safety Requirements:**
- Full type hints on all public APIs
- @runtime_checkable on ComponentLookup protocol
- Type-safe dict[str, type] storage in ComponentNameRegistry
- Generic type support for injector calls

**Thread Safety:**
- ComponentNameRegistry must be thread-safe for free-threaded Python
- Use appropriate locking mechanisms for concurrent access
- Follow Python 3.14 free-threading best practices
