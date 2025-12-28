# Spec Requirements: Basic svcs Container Integration

## Initial Description
Create adapter layer that bridges tdom's component system with svcs container, implement DefaultInjector that resolves component dependencies from container, and add container initialization helpers.

**Size:** S (Small)

**Status:** [ ] Not Started

**Dependencies:**
- Item 1: Minimal tdom Core Hooks (completed)

**Position in Roadmap:**
- This is a foundation item that enables core DI functionality
- Required before items 3-7 can be implemented

## Requirements Discussion

### First Round Questions

**Q1:** I assume the adapter layer should expose a single primary integration point (like a `Container` wrapper class) that tdom components interact with, rather than exposing raw svcs APIs directly to template code. Is that correct, or should templates have direct svcs access?

**Answer:** No, keep raw - templates should have direct svcs access, not wrapped

**Q2:** For the DefaultInjector, I'm thinking it should resolve dependencies using type hints from component function signatures (similar to how FastAPI does dependency injection). Should we support both positional and keyword argument injection, or just keyword args?

**Answer:** Follow what DefaultInjector/KeywordInjector/HopscotchInjector do. Ask the container for the registered injector.

**Q3:** I assume container initialization helpers should include a factory function like `create_container(registry: svcs.Registry) -> Container` that sets up the tdom-svcs adapter with sensible defaults. Should this also include helpers for common service registration patterns (singletons, request-scoped, etc.)?

**Answer:** Sure - yes to factory function with sensible defaults

**Q4:** For the adapter layer, should it handle only synchronous component resolution initially, or do we need to support async components from the start? (Given this is a "Small" task, I'm leaning toward sync-only initially.)

**Answer:** Let's also do async - support both sync and async components

**Q5:** I'm thinking the DefaultInjector should raise clear, actionable errors when a requested service isn't registered in the container (e.g., "Service 'DatabaseConnection' not found in container. Did you forget to register it?"). Should we also provide suggestions based on similar registered service names?

**Answer:** Yes - clear, actionable errors with suggestions for similar service names

**Q6:** Should the container initialization include automatic registration of commonly-needed services (like the container itself for self-injection), or should users explicitly register everything they need?

**Answer:** Register the services we define in this package. ComponentFactory, ComponentLocator, etc.

**Q7:** Given that Item 1 (Minimal tdom Core Hooks) is complete, I assume we'll be implementing the hooks interface that was defined there. Should the adapter layer use those hooks to intercept component creation, or will it provide an alternative integration point?

**Answer:** Intercept and then get the service from the container that implements it (use hooks from Item 1)

**Q8:** What should be explicitly excluded from this implementation? For example: keyword overrides (that's Item 5), decorator-based discovery (that's Item 3), resource-based resolution (Items 6-7), async support, or middleware hooks (Item 9)?

**Answer:** Correct - exclude keyword overrides (Item 5), decorator-based discovery (Item 3), resource-based resolution (Items 6-7), and middleware hooks (Item 9)

### Existing Code to Reference

**Similar Features Identified:**

- **Item 1 Implementation**: `/Users/pauleveritt/projects/t-strings/tdom-svcs/agent-os/specs/2025-12-27-core-tdom-integration-hooks/`
  - ComponentLookup protocol definition from tdom-svcs wrapper
  - Config protocol with component_lookup attribute
  - Manual verification showing protocol usage pattern
  - Integration points: config and context parameters threading through html() → _resolve_t_node() → _invoke_component()

- **svcs-di Injector Patterns**: `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/`
  - `auto.py`: DefaultInjector and DefaultAsyncInjector implementations showing two-tier precedence (container.get() then defaults)
  - `injectors/keyword.py`: KeywordInjector showing three-tier precedence pattern (kwargs, container, defaults)
  - `injectors/locator.py`: HopscotchInjector extending KeywordInjector with ServiceLocator integration
  - FieldInfo extraction and resolution patterns using get_field_infos()
  - Container retrieval: `container.get(Injector)` pattern with fallback construction

- **ServiceLocator Pattern**: `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/locator.py`
  - ServiceLocator as immutable registry for multiple implementations
  - Resource-based and location-based matching with precedence scoring
  - Registration pattern: `locator.register(service_type, implementation, resource=..., location=...)`
  - Package scanning with @injectable decorator for auto-discovery

### Follow-up Questions

**Follow-up 1:** You mentioned "Register the services we define in this package. ComponentFactory, ComponentLocator, etc." - Should these services be auto-registered when the tdom-svcs package is imported, or should users explicitly register them in their application setup code?

**Answer:** Add a `services.setup_container(container: Container) -> None` function (explicit setup, not auto-registration)

**Follow-up 2:** You said to "ask the container for the registered injector." Should the adapter layer expect users to register their chosen injector type explicitly in the container, or should there be a fallback/default if no injector is registered?

**Answer:** (Clarified through architectural discussion - see below)

**Follow-up 3:** From Item 1, I see the hooks use `ComponentLookup` protocol with `__call__(name: str, context: Mapping[str, Any]) -> Callable | None`. Should our adapter implement this protocol directly, or create a separate adapter class that bridges between ComponentLookup and the svcs injector pattern?

**Answer:** Implement ComponentLookup protocol directly (no separate adapter class)

**Follow-up 4:** When a template uses `<{Button} .../>`, the ComponentLookup receives the name "Button" as a string. How should the adapter map this string name back to the actual service type for container resolution?

**Answer:** Option A - Put a service in the registry that tracks names and symbols (component name registry service)

**Follow-up 5:** Looking at the svcs-di patterns, services are typically registered as factories in the Registry. Should component classes be registered as factories, direct value registrations, through ServiceLocator, or some combination?

**Answer:** Use a helper function for registration (registers name→type mapping). Later, a decorator can be syntactic sugar for this helper. Defer decorator to Item 3.

**Follow-up 6:** Should this basic integration depend on HopscotchInjector, or work with any injector?

**Answer:** At minimum KeywordInjector since components have "props" that need to be part of the instantiation.

**Follow-up 7:** Should ComponentLookup support multi-implementation logic (resource-based, location-based)?

**Answer:** Simplest case - string name → single component type → injector construction

## Visual Assets

### Files Provided:
No visual files found.

### Visual Insights:
No visual assets provided.

## Requirements Summary

### Functional Requirements

**Core Integration:**
- Implement ComponentLookup protocol from Item 1 directly in tdom-svcs
- ComponentLookup receives string component names from tdom's hook system
- Map string names to type objects using a ComponentNameRegistry service
- Retrieve injector from container (minimum KeywordInjector)
- Use injector to construct component instances with props/dependencies
- Support both sync and async component construction

**Container Setup:**
- Provide `services.setup_container(container: Container) -> None` helper function
- Auto-register internal services during setup:
  - ComponentNameRegistry (maps str → type)
  - ComponentLookup implementation
  - Any other internal services needed
- Users must explicitly call setup_container() in application initialization
- Do NOT auto-register on package import

**Component Registration:**
- Provide helper function for registering components: `register_component(registry, name: str, component_type: type)`
- Helper registers both:
  1. Name→type mapping in ComponentNameRegistry
  2. Component factory in svcs Registry (using injector pattern)
- Defer decorator-based registration (@component) to Item 3

**Error Handling:**
- Clear, actionable error messages when component not found
- Suggest similar component names based on registered components
- Helpful errors when injector not found in container
- Helpful errors when ComponentNameRegistry not set up

**Integration with tdom Hooks:**
- ComponentLookup.__call__(name: str, context: Mapping[str, Any]) receives string name from tdom
- Look up type from ComponentNameRegistry
- Get injector from container
- Construct component using injector
- Return callable component or None if not found
- Context parameter available for future use (not needed for basic integration)

### Reusability Opportunities

**Existing Patterns to Follow:**
- DefaultInjector/DefaultAsyncInjector pattern from svcs-di/auto.py for injector structure
- KeywordInjector pattern for three-tier precedence (kwargs, container, defaults)
- FieldInfo extraction using get_field_infos() for analyzing component signatures
- Container retrieval pattern: `container.get(InjectorType)` with fallback construction
- ServiceLocator registration pattern for future multi-implementation support

**Similar Code to Reference:**
- Item 1 verification script showing ComponentLookup protocol implementation pattern
- svcs-di injector implementations for dependency resolution logic
- Mock ComponentLookup from manual_verification.py showing protocol satisfaction without inheritance

**Integration Points:**
- tdom's html() function with config and context parameters (from Item 1)
- ComponentLookup protocol definition (from Item 1's tdom-svcs wrapper)
- svcs.Container and svcs.Registry for service management
- KeywordInjector at minimum for component construction with props

### Scope Boundaries

**In Scope:**
- ComponentLookup protocol implementation
- ComponentNameRegistry service for str→type mapping
- setup_container() helper function
- register_component() helper function
- Injector retrieval from container
- Both sync and async component construction
- Clear error messages with suggestions
- Simple single-implementation resolution (one component type per name)
- Raw svcs Container exposure (no wrapper)

**Out of Scope:**
- @component decorator (deferred to Item 3: @Inject Decorator and Component Discovery)
- Keyword override support (deferred to Item 5: KeywordInjector with Props Override)
- Package scanning/auto-discovery (deferred to Item 3)
- Resource-based component resolution (deferred to Item 6)
- Location-based component resolution (deferred to Item 7)
- Multi-implementation resolution logic (deferred to Items 6-7)
- Middleware hooks or component lifecycle events (deferred to Item 9)
- Testing utilities/mock injection (deferred to Item 8)
- Custom injector implementations beyond using existing KeywordInjector
- Automatic service registration on import (must be explicit via setup_container)

### Technical Considerations

**Dependencies:**
- Python 3.14+ (PEP 750 t-strings)
- svcs for service container
- svcs-di for KeywordInjector and dependency injection primitives
- tdom for component system with hooks from Item 1

**Integration Constraints:**
- Must work with tdom's ComponentLookup protocol (string name input, callable output)
- Must integrate with svcs container without wrapping or hiding it
- Must support tdom's context parameter (Mapping[str, Any]) even if unused initially
- Must work with KeywordInjector's three-tier precedence for component props

**Architecture Decisions:**
- No wrapper around svcs - expose raw Container
- Direct ComponentLookup protocol implementation (no adapter class)
- Component name registry as a service in the container
- Helper function pattern for registration (decorator comes later)
- Minimum KeywordInjector dependency for prop support
- Simple resolution only (no multi-implementation logic)

**Type Safety:**
- Full type hints for all public APIs
- ComponentLookup protocol with runtime_checkable decorator
- ComponentNameRegistry with type-safe dict[str, type] storage
- Generic type support for injector calls: injector(ComponentType)

**Error Handling Strategy:**
- Component not found: suggest similar names from registry
- Injector not found: guide user to register injector or call setup_container()
- ComponentNameRegistry not found: indicate setup_container() not called
- Type resolution errors: include component name and expected signature
