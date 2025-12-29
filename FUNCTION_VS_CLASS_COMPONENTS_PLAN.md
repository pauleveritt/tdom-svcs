# Plan: Function vs Class Components Policy

## Policy Statement

This project enforces clear distinctions between function and class components, and between different injector types:

### ✅ Class Components (Dataclasses)
- **CAN** use `Inject[]` for dependency injection
- **CAN** be registered by string name in ComponentNameRegistry
- **CAN** be discovered via `@injectable` decorator and `scan_components()`
- **CAN** be resolved via ComponentLookup by string name
- **SHOULD** use **HopscotchInjector** in examples and documentation

### ✅ Function Components
- **CAN** use `Inject[]` for dependency injection
- **CANNOT** be registered by string name in ComponentNameRegistry
- **CANNOT** use `@injectable` decorator (svcs-di enforces this)
- **CANNOT** be discovered via `scan_components()`
- **CANNOT** be resolved via ComponentLookup by string name
- **SHOULD** use **KeywordInjector** in examples (simple cases only, no ComponentLookup)

### 🔧 Injector Usage Policy

#### KeywordInjector (Simple Function Components Only)
- **USE FOR:** Simple function component examples with direct injection
- **USE WHEN:** No ComponentLookup or string name resolution needed
- **EXAMPLE:** Direct function call with `Inject[]` parameters
- **NO ComponentLookup:** Functions cannot be looked up by string name

#### HopscotchInjector (All Other Cases)
- **USE FOR:** Class components, ComponentLookup integration, production patterns
- **USE WHEN:** Components registered by string name, multi-implementation scenarios
- **SUPPORTS:** Resource-based resolution (`resource=X`), location-based resolution (`location=PurePath`)
- **DEFAULT:** This is the primary injector for tdom-svcs

### Rationale
- **String name lookup** is for reusable, discoverable components → classes only
- **Inject[] dependency injection** is a general pattern → works for both
- **KeywordInjector** is educational → shows simplest DI case with functions
- **HopscotchInjector** is production-ready → supports advanced resolution strategies
- **Consistency with svcs-di:** The `@injectable` decorator in svcs-di already enforces class-only decoration
- **Template usage:** Templates reference components by name (`<Button>`) → requires class components
- **Direct usage:** Functions can still use Inject[] when called directly (not via templates)

## Why HopscotchInjector for Production?

### Technical Capabilities

**HopscotchInjector** provides advanced resolution strategies that KeywordInjector lacks:

1. **Resource-based Resolution**
   - Components can be registered with `resource=CustomerContext`
   - Different implementations selected based on request context
   - Enables multi-tenancy, feature flags, A/B testing
   - Example: `CustomerDashboard` vs `AdminDashboard` based on user context

2. **Location-based Resolution**
   - Components can be registered with `location=PurePath("/admin")`
   - Different implementations for different URL paths
   - Enables route-specific components
   - Example: `AdminPanel` only resolves at `/admin` routes

3. **Multi-implementation Support**
   - Multiple implementations of same component type
   - Automatic selection based on context
   - Critical for enterprise applications

### KeywordInjector Limitations

**KeywordInjector** is intentionally simple:
- ✅ Basic dependency injection via `Inject[]`
- ✅ Keyword argument override support
- ❌ No resource-based resolution
- ❌ No location-based resolution
- ❌ No multi-implementation support

**Use case:** Educational examples showing how `Inject[]` works with functions (no ComponentLookup needed)

### ComponentLookup Integration

ComponentLookup requires the advanced capabilities of HopscotchInjector:
- Resolves components by string name → needs resource/location awareness
- Works with `@injectable(resource=X, location=Y)` → requires HopscotchInjector
- Production-ready component resolution → must support all resolution strategies

**Therefore:** ComponentLookup MUST use HopscotchInjector, not KeywordInjector

## Current State Analysis

### ✅ Already Correct
1. **svcs-di's @injectable decorator** - Already enforces class-only in decorators.py
2. **Component decorator discovery spec** - States "@injectable can only be applied to classes, not functions"
3. **scan_components()** - Only discovers @injectable decorated classes
4. **All current examples** - Show only class components with Inject[]

### ⚠️ Needs Clarification/Update

#### Component Type Policy Issues
1. **basic-svcs-container-integration spec** - Says "Support both dataclass components and function components" for register_component()
2. **Documentation** - Doesn't explicitly state that Inject[] works on functions too
3. **Examples** - Missing examples of function components using Inject[] (without string name registration)
4. **Code comments** - Could be clearer about the policy

#### Injector Usage Issues
1. **ComponentLookup implementation** - Currently uses KeywordInjector instead of HopscotchInjector
2. **All specs** - Show KeywordInjector in examples that should use HopscotchInjector
3. **All examples** - Use KeywordInjector for class components (should use HopscotchInjector)
4. **All tests** - Use KeywordInjector for class components (should use HopscotchInjector)
5. **Mission.md** - Mentions KeywordInjector for "prop overrides" but should clarify it's only for simple function examples
6. **Documentation** - Doesn't explain when to use KeywordInjector vs HopscotchInjector
7. **README.md** - Needs examples showing correct injector usage

## Implementation Plan

### Phase 0: Update Injector Usage Throughout Project

#### 0.1 Update ComponentLookup to use HopscotchInjector
**File:** `src/tdom_svcs/services/component_lookup/component_lookup.py`

**Changes:**
- Replace `KeywordInjector` and `KeywordAsyncInjector` imports with `HopscotchInjector` and `HopscotchAsyncInjector`
- Update `_construct_sync_component()` to use `HopscotchInjector`
- Update `_construct_async_component()` to use `HopscotchAsyncInjector`
- Update docstrings to reference HopscotchInjector instead of KeywordInjector
- Update error messages in exceptions.py to reference correct injector names

#### 0.2 Update Mission and Roadmap
**Files:**
- `agent-os/product/mission.md`
- `agent-os/product/roadmap.md`

**Changes in mission.md:**
- Line 107-109: Update KeywordInjector description to clarify it's for simple function examples only
- Add clarity: "KeywordInjector for educational function component examples"
- Emphasize: "HopscotchInjector as the primary production injector"

**Changes in roadmap.md:**
- Review all items for injector mentions
- Ensure consistency with HopscotchInjector as primary injector

#### 0.3 Update README with correct injector examples
**File:** `README.md`

**Changes:**
- Add "Quick Start" section showing HopscotchInjector with class components
- Add separate "Function Components" section showing KeywordInjector (simple, no ComponentLookup)
- Clarify when to use each injector type
- Show ComponentLookup integration with HopscotchInjector

#### 0.4 Update all spec documents
**Files:**
- `agent-os/specs/2025-12-28-basic-svcs-container-integration/spec.md`
- `agent-os/specs/2025-12-28-basic-svcs-container-integration/tasks.md`
- `agent-os/specs/2025-12-28-basic-svcs-container-integration/planning/requirements.md`
- `agent-os/specs/2025-12-28-component-decorator-discovery/spec.md`
- `agent-os/specs/2025-12-28-component-lifecycle-middleware-system/spec.md`
- Any verification documents

**Changes:**
- Replace KeywordInjector with HopscotchInjector in all class component examples
- Keep KeywordInjector only in simple function component examples (if any)
- Update all code examples to use correct injector
- Update requirements and acceptance criteria to reference HopscotchInjector
- Update task descriptions and implementation notes

#### 0.5 Update all example files
**Files:**
- `examples/component_discovery.py`
- `examples/resource_based_components.py`
- `examples/location_based_components.py`
- `examples/direct_decorator_application.py`
- Any other example files

**Changes:**
- Replace `from svcs_di.injectors.keyword import KeywordInjector` with `from svcs_di.injectors.hopscotch import HopscotchInjector`
- Update injector instantiation
- Update comments to explain HopscotchInjector usage
- Add one simple example showing KeywordInjector with function component (no ComponentLookup)

#### 0.6 Update all test files
**Files:**
- `tests/services/test_component_lookup.py`
- `tests/test_component_lookup_integration.py`
- `tests/test_component_discovery_edge_cases.py`
- `tests/test_scan_components.py`
- Any other test files using injectors

**Changes:**
- Replace KeywordInjector with HopscotchInjector in all tests
- Replace KeywordAsyncInjector with HopscotchAsyncInjector
- Update test fixtures
- Update test assertions
- Keep tests focused on behavior, not implementation details

#### 0.7 Update docstrings and module documentation
**Files:**
- `src/tdom_svcs/scanning.py` (large module docstring)
- Any other files with extensive documentation

**Changes:**
- Replace KeywordInjector references with HopscotchInjector
- Add explanation of when to use each injector type
- Update code examples in docstrings

#### 0.8 Update standards documents
**File:** `agent-os/standards/global/services.md`

**Changes:**
- Update injector usage guidelines
- Clarify KeywordInjector (simple functions) vs HopscotchInjector (everything else)

### Phase 1: Update Component Type Policy in Specs and Documentation

#### 1.1 Update basic-svcs-container-integration spec
**File:** `agent-os/specs/2025-12-28-basic-svcs-container-integration/spec.md`

**Changes:**
- Line 41: Change "Support both dataclass components and function components" to "Support only class (dataclass) components for name registration"
- Add new section "Function Components vs Class Components" explaining:
  - Function components CAN use Inject[] but CANNOT be registered by name
  - Class components CAN use both Inject[] AND be registered by name
  - This is because string name lookup is for template-referenceable components

#### 1.2 Update basic-svcs-container-integration tasks
**File:** `agent-os/specs/2025-12-28-basic-svcs-container-integration/tasks.md`

**Changes:**
- Line 134: Change "Support both dataclass components and function components" to "Support only class components (validate dataclass or class with __init__)"
- Line 140: Change "Verify register_component works for both dataclass and function components" to "Verify register_component validates class-only and rejects functions"

#### 1.3 Update basic-svcs-container-integration requirements
**File:** `agent-os/specs/2025-12-28-basic-svcs-container-integration/planning/requirements.md`

**Changes:**
- Add clarification that register_component only accepts classes
- Document the distinction between Inject[] usage (both) and name registration (classes only)

#### 1.4 Add policy section to component-decorator-discovery spec
**File:** `agent-os/specs/2025-12-28-component-decorator-discovery/spec.md`

**Changes:**
- Add new section after "Specific Requirements" titled "Component Type Policy"
- Explain function vs class component distinctions
- Clarify that Inject[] works on both, but only classes can be registered by name

#### 1.5 Create example of function component with Inject[]
**File:** `examples/function_component_with_inject.py` (NEW)

**Content:**
- Show a function component using Inject[] for dependency injection
- Explain that it cannot be registered by string name
- Explain that it must be called directly (not via template string lookup)
- Show comparison with equivalent class component that CAN be registered

### Phase 2: Update Code and Validation

#### 2.1 Add validation to register_component (if it exists)
**File:** Check if `src/tdom_svcs/services/__init__.py` has register_component function

**Changes:**
- If function exists, add validation to ensure component_type is a class
- Raise clear TypeError if a function is passed: "register_component only accepts class components. Function components can use Inject[] but cannot be registered by string name."

#### 2.2 Update ComponentNameRegistry documentation
**File:** `src/tdom_svcs/services/component_registry/component_name_registry.py`

**Changes:**
- Add docstring clarification that registry is for class components only
- Update register() method docstring to state component_type should be a class

#### 2.3 Update ComponentNameRegistry protocol
**File:** `src/tdom_svcs/services/component_registry/models.py`

**Changes:**
- Update protocol docstring to clarify "class components" not just "components"
- Update method docstrings to be explicit about class types

#### 2.4 Add comment to ComponentLookup
**File:** `src/tdom_svcs/services/component_lookup/component_lookup.py`

**Changes:**
- Add class docstring note: "Note: ComponentLookup resolves class components by string name. Function components can use Inject[] but cannot be looked up by name."

### Phase 3: Add Tests

#### 3.1 Test function rejection in register_component
**File:** Create test to verify register_component rejects functions

**Test:**
```python
def test_register_component_rejects_function():
    """Test that register_component raises error for function components."""
    registry = svcs.Registry()
    component_registry = ComponentNameRegistry()
    container = svcs.Container(registry)

    def my_function_component():
        return "hello"

    with pytest.raises(TypeError, match="only accepts class components"):
        register_component(registry, container, "MyFunc", my_function_component)
```

#### 3.2 Add example test for function with Inject[]
**File:** `tests/test_function_components_with_inject.py` (NEW)

**Test:**
- Show that a function with Inject[] parameters works when called directly
- Show that it cannot be registered by name
- Show that KeywordInjector can construct it

### Phase 4: Update Related Specs

#### 4.1 Check component-lifecycle-middleware spec
**File:** `agent-os/specs/2025-12-28-component-lifecycle-middleware-system/spec.md`

**Changes:**
- Ensure middleware documentation is clear about class vs function components
- Middleware should work with both (via Inject[]) but string lookup only works with classes

#### 4.2 Update roadmap if needed
**File:** `agent-os/product/roadmap.md`

**Changes:**
- Review items 4-12 for any mention of "components" that should clarify "class components"

## Summary

### Before
- Ambiguous about whether functions can be registered by name
- Not clear that Inject[] works on both functions and classes
- Specs and code had minor inconsistencies
- **KeywordInjector used everywhere** (incorrect for production use)
- ComponentLookup uses KeywordInjector (should use HopscotchInjector)
- No clear guidance on when to use each injector
- **Recurring type errors:** `Expected type[T], got type`
- ComponentNameRegistry accepts `type | Callable` (violates policy)
- Type casts everywhere (ComponentLookup uses `cast()` instead of generics)
- No validation at registration time (fails late)

### After
- **Clear component policy:** Classes for name lookup, Inject[] for both
- **Clear injector policy:** KeywordInjector for simple function examples only, HopscotchInjector for all other cases
- **Clear type policy:** Use `type[T]` generics, validate early, no casts
- **Specs updated:** All specs explicitly state class-only for name registration
- **Code updated:** ComponentLookup uses HopscotchInjector and `type[T]` generics
- **Examples updated:** Show correct injector for each use case
- **Tests updated:** Use HopscotchInjector for class components
- **Documentation updated:** Clear guidance on injector selection
- **Type validation:** ComponentNameRegistry rejects functions at registration time
- **No type errors:** Type checker understands `type[T]` properly throughout codebase

## Files to Modify

### Phase 0: Injector Updates

#### Product Documentation
1. `agent-os/product/mission.md` - Update KeywordInjector description
2. `agent-os/product/roadmap.md` - Review injector mentions
3. `README.md` - Add quick start with correct injectors

#### Spec Documents
4. `agent-os/specs/2025-12-28-basic-svcs-container-integration/spec.md`
5. `agent-os/specs/2025-12-28-basic-svcs-container-integration/tasks.md`
6. `agent-os/specs/2025-12-28-basic-svcs-container-integration/planning/requirements.md`
7. `agent-os/specs/2025-12-28-component-decorator-discovery/spec.md`
8. `agent-os/specs/2025-12-28-component-lifecycle-middleware-system/spec.md`
9. Verification documents in spec folders

#### Core Code
10. `src/tdom_svcs/services/component_lookup/component_lookup.py` - Use HopscotchInjector
11. `src/tdom_svcs/services/component_lookup/exceptions.py` - Update error messages
12. `src/tdom_svcs/scanning.py` - Update module docstring

#### Examples
13. `examples/component_discovery.py`
14. `examples/resource_based_components.py`
15. `examples/location_based_components.py`
16. `examples/direct_decorator_application.py`
17. `examples/function_component_simple.py` (NEW - KeywordInjector example)

#### Tests
18. `tests/services/test_component_lookup.py`
19. `tests/test_component_lookup_integration.py`
20. `tests/test_component_discovery_edge_cases.py`
21. `tests/test_scan_components.py`

#### Standards
22. `agent-os/standards/global/services.md`
23. `.claude/instructions.md` (NEW - Project rules and guidelines)

### Phase 1: Component Type Policy

#### Documentation Updates
23. `agent-os/specs/2025-12-28-basic-svcs-container-integration/spec.md` - Component type policy
24. `agent-os/specs/2025-12-28-basic-svcs-container-integration/tasks.md` - Update tasks
25. `agent-os/specs/2025-12-28-basic-svcs-container-integration/planning/requirements.md` - Add policy
26. `agent-os/specs/2025-12-28-component-decorator-discovery/spec.md` - Add policy section

#### Code Updates
27. `src/tdom_svcs/services/__init__.py` (if register_component exists)
28. `src/tdom_svcs/services/component_registry/component_name_registry.py` - Update docs
29. `src/tdom_svcs/services/component_registry/models.py` - Update protocol docs

#### Examples and Tests
30. `examples/function_component_with_inject.py` (NEW - function with Inject[])
31. Test file for register_component function rejection (NEW)
32. `tests/test_function_components_with_inject.py` (NEW)

### Phase 5: Type Hinting Fixes (HIGHEST PRIORITY)

#### Core Code (Type System Changes)
33. `src/tdom_svcs/services/component_registry/component_name_registry.py` - Remove Callable, add validation, use `type` only
34. `src/tdom_svcs/services/component_registry/models.py` - Update protocol docstrings for class-only
35. `src/tdom_svcs/services/component_lookup/component_lookup.py` - Add TypeVar, use `type[T]`, eliminate casts
36. `src/tdom_svcs/scanning.py` - Add isinstance() validation before registration

#### Tests (Type Validation Tests)
37. `tests/services/test_component_lookup.py` - Add tests for function rejection, update type hints
38. `tests/test_component_lookup_integration.py` - Ensure all use class components
39. `tests/test_scan_components.py` - Test class validation in scanning
40. `tests/services/test_component_name_registry.py` - Test TypeError on function registration

#### Examples (Type Correctness)
41. All examples - Verify proper type hints (should be correct already)
42. Add example showing function rejection error

#### Documentation & Configuration
43. Update all specs to mention class-only validation
44. `.claude/instructions.md` - Add type hinting best practices section
45. `pyproject.toml` - Add mypy configuration (optional)
46. `.github/workflows/` - Add mypy to CI (optional)

## Verification Checklist

### Injector Usage (Phase 0)
- [ ] ComponentLookup uses HopscotchInjector (not KeywordInjector)
- [ ] ComponentLookup uses HopscotchAsyncInjector (not KeywordAsyncInjector)
- [ ] Mission.md clarifies KeywordInjector is for simple function examples only
- [ ] README.md shows HopscotchInjector in quick start examples
- [ ] All spec documents use HopscotchInjector for class components
- [ ] All examples use HopscotchInjector for class components
- [ ] All tests use HopscotchInjector for class components
- [ ] One example exists showing KeywordInjector with simple function (no ComponentLookup)
- [ ] Module docstrings updated to reference correct injectors
- [ ] Standards document clarifies injector usage policy
- [ ] Claude instructions file documents injector policy and example structure
- [ ] No KeywordInjector references in ComponentLookup-related code/docs

### Component Type Policy (Phase 1+)
- [ ] All specs explicitly state class-only for name registration
- [ ] All specs explicitly state Inject[] works for both functions and classes
- [ ] register_component() rejects functions with clear error message
- [ ] ComponentNameRegistry documentation clarifies class components only
- [ ] Example shows function component using Inject[] without name registration
- [ ] Example shows class component using Inject[] with name registration
- [ ] Test verifies function rejection by register_component
- [ ] Test verifies function with Inject[] works when called directly
- [ ] All existing tests still pass
- [ ] No ambiguity in any documentation about function vs class usage

### Overall Verification
- [ ] All tests pass after injector changes
- [ ] Examples run successfully with HopscotchInjector
- [ ] Documentation is consistent across all files
- [ ] No references to "KeywordInjector" in class component contexts
- [ ] Clear distinction between educational (KeywordInjector) and production (HopscotchInjector) patterns
- [ ] No type checker errors (`Expected type[T], got type`)
- [ ] ComponentNameRegistry enforces class-only policy at registration time

## Next Steps

1. Review this plan with stakeholders
2. Get approval on all policies (component types + injector usage + type hinting)
3. **PRIORITY 1:** Execute Phase 5 (type hinting fixes) - fixes root cause of type errors
4. **PRIORITY 2:** Execute Phase 0 (injector updates) - critical for production correctness
5. Execute Phases 1-4 for component type policy clarifications
6. Run full test suite after each phase to verify no regressions
7. Update any additional documentation discovered during implementation

## Priority Order

**Phase 5 (Type Hinting) is HIGHEST PRIORITY** because:
- Fixes recurring `Expected type[T], got type` errors throughout codebase
- Enforces class-only policy at type level (impossible to register functions)
- Eliminates all type casts and uses proper generics
- Benefits all other phases (better type safety)
- Solves the problem "once and for all" as requested

**Phase 0 (Injector Updates) is SECOND PRIORITY** because:
- ComponentLookup is using the wrong injector (KeywordInjector instead of HopscotchInjector)
- All production code should use HopscotchInjector for class components
- KeywordInjector lacks support for resource and location-based resolution
- This affects all existing examples, tests, and documentation

**Phases 1-4** can follow as documentation/policy clarifications and will be easier with proper type hinting in place.

---

# ADDENDUM: Type Hinting Problem Analysis and Solution

## Problem Statement

We have a recurring type checking error: `Expected type 'type[T]', got 'type' instead`

This appears in code like:
```python
component_type = registry.get_type(name)  # Returns: type | Callable | None
component_class = cast(type, component_type)  # Cast to: type
return injector(component_class)  # ERROR: Expected type[T], got type
```

### Root Causes

1. **Mixing `type` and `type[T]`**
   - `type` is the base metaclass (non-generic)
   - `type[T]` is a generic type expecting a specific class type
   - Type checkers treat these as incompatible

2. **`Callable` in ComponentNameRegistry**
   - Registry accepts `type | Callable` but we only support class components
   - This violates our component type policy (class-only for name registration)
   - Adds unnecessary union complexity

3. **No Generic Type Parameters**
   - ComponentLookup doesn't use TypeVar/Generic
   - Injectors expect `type[T]` but receive plain `type`
   - No way to preserve type information through the chain

4. **Late Type Assertions**
   - Type casting happens too late (in ComponentLookup)
   - Should validate and assert types early (in ComponentNameRegistry)
   - Helpers should assume they receive correct types

## Comprehensive Solution

### Phase 5: Fix Type Hinting Throughout Project

#### 5.1 Remove `Callable` from ComponentNameRegistry

**Problem:** Registry accepts `type | Callable` but policy says class-only for name registration

**File:** `src/tdom_svcs/services/component_registry/component_name_registry.py`

**Changes:**
```python
# BEFORE
_registry: dict[str, type | Callable] = field(default_factory=dict, init=False, repr=False)

def register(self, name: str, component_type: type | Callable) -> None:
    """Register a component type under a string name."""
    with self._lock:
        self._registry[name] = component_type

def get_type(self, name: str) -> type | Callable | None:
    """Retrieve a component type by its registered name."""
    with self._lock:
        return self._registry.get(name)

# AFTER
from typing import TypeGuard

_registry: dict[str, type] = field(default_factory=dict, init=False, repr=False)

def register(self, name: str, component_type: type) -> None:
    """
    Register a component class type under a string name.

    Args:
        name: The string name to register the component under
        component_type: The component class type to register (must be a class, not a function)

    Raises:
        TypeError: If component_type is not a class
    """
    # Validation: ensure it's actually a class
    if not isinstance(component_type, type):
        raise TypeError(
            f"ComponentNameRegistry only accepts class types, got {type(component_type).__name__}. "
            f"Function components cannot be registered by string name."
        )

    with self._lock:
        self._registry[name] = component_type

def get_type(self, name: str) -> type | None:
    """
    Retrieve a component class type by its registered name.

    Args:
        name: The string name of the component to look up

    Returns:
        The component class type if found, None otherwise
    """
    with self._lock:
        return self._registry.get(name)
```

**Rationale:**
- Enforces class-only policy at registration time (fail fast)
- Eliminates `Callable` from type signatures
- Provides clear error message about function vs class components
- Type checker knows we only deal with `type`, not `type | Callable`

#### 5.2 Update ComponentNameRegistry Protocol

**File:** `src/tdom_svcs/services/component_registry/models.py`

**Changes:**
```python
# BEFORE
def register(self, name: str, component_type: type) -> None:
    """Register a component type under a string name."""
    ...

def get_type(self, name: str) -> type | None:
    """Retrieve a component type by its registered name."""
    ...

# AFTER
def register(self, name: str, component_type: type) -> None:
    """
    Register a component class type under a string name.

    Args:
        name: The string name to register the component under
        component_type: The component class type (must be a class, not a function)

    Raises:
        TypeError: If component_type is not a class
    """
    ...

def get_type(self, name: str) -> type | None:
    """
    Retrieve a component class type by its registered name.

    Args:
        name: The string name of the component to look up

    Returns:
        The component class type if found, None otherwise
    """
    ...
```

**Note:** Protocol already uses `type`, not `type | Callable`, which is correct.

#### 5.3 Add Generic Type Parameters to ComponentLookup

**Problem:** ComponentLookup uses `cast(type, ...)` but type checkers want `type[T]`

**File:** `src/tdom_svcs/services/component_lookup/component_lookup.py`

**Changes:**
```python
# BEFORE
from typing import Any, Callable, Coroutine, cast

def __call__(
    self, name: str, context: Mapping[str, Any]
) -> Callable | Coroutine[Any, Any, Any] | None:
    # ... setup code ...

    # Type assertion: injectors require type, not Callable
    component_class = cast(type, component_type)

    # Step 4 & 5: Retrieve injector and construct component
    if is_async:
        return self._construct_async_component(component_class)
    else:
        return self._construct_sync_component(component_class)

def _construct_sync_component(self, component_type: type) -> Callable:
    """Construct a synchronous component using HopscotchInjector."""
    try:
        injector = self.container.get(HopscotchInjector)
    except svcs.exceptions.ServiceNotFoundError:
        raise InjectorNotFoundError("HopscotchInjector", is_async=False)

    return cast(Callable, injector(component_type))

# AFTER
from typing import Any, Callable, Coroutine, TypeVar, cast

# TypeVar for component types
T = TypeVar("T")

def __call__(
    self, name: str, context: Mapping[str, Any]
) -> Callable | Coroutine[Any, Any, Any] | None:
    # ... setup code ...

    # Step 2: Look up component type by name
    component_type = registry.get_type(name)
    if component_type is None:
        raise ComponentNotFoundError(name)

    # component_type is guaranteed to be `type` (not None, not Callable)
    # Assert it's a class for type checker
    assert isinstance(component_type, type), f"Expected class, got {type(component_type)}"

    # Step 3: Detect if component is async
    is_async = inspect.iscoroutinefunction(component_type)

    # Step 4 & 5: Retrieve injector and construct component
    if is_async:
        return self._construct_async_component(component_type)
    else:
        return self._construct_sync_component(component_type)

def _construct_sync_component(self, component_type: type[T]) -> T:
    """
    Construct a synchronous component using HopscotchInjector.

    Args:
        component_type: The component class type to construct

    Returns:
        The constructed component instance

    Raises:
        InjectorNotFoundError: If HopscotchInjector not in container
    """
    try:
        injector = self.container.get(HopscotchInjector)
    except svcs.exceptions.ServiceNotFoundError:
        raise InjectorNotFoundError("HopscotchInjector", is_async=False)

    # injector(component_type) now correctly receives type[T] and returns T
    return injector(component_type)

def _construct_async_component(
    self, component_type: type[T]
) -> Coroutine[Any, Any, T]:
    """
    Construct an asynchronous component using HopscotchAsyncInjector.

    Args:
        component_type: The async component class type to construct

    Returns:
        Coroutine that resolves to the constructed component instance

    Raises:
        InjectorNotFoundError: If HopscotchAsyncInjector not in container
    """
    try:
        injector = self.container.get(HopscotchAsyncInjector)
    except svcs.exceptions.ServiceNotFoundError:
        raise InjectorNotFoundError("HopscotchAsyncInjector", is_async=True)

    # injector(component_type) returns Coroutine[Any, Any, T]
    return injector(component_type)
```

**Key Improvements:**
- Use `type[T]` instead of plain `type` in helper methods
- Add TypeVar `T` to preserve type information
- Replace `cast()` with runtime `assert isinstance()` for validation
- Remove unnecessary casts in return statements
- Type checker now understands: `injector(type[T])` → `T`

#### 5.4 Add Validation to scan_components()

**Problem:** scan_components() might register non-class types from decorated items

**File:** `src/tdom_svcs/scanning.py`

**Changes:**
```python
# Add validation when registering discovered components
def scan_components(
    registry: svcs.Registry,
    component_name_registry: ComponentNameRegistry,
    *packages: str | ModuleType,
) -> None:
    """Scan packages for @injectable components and register them."""

    # ... existing scan() call ...

    # Collect decorated items and register in ComponentNameRegistry
    for package in packages_list:
        # ... module discovery ...

        for item in decorated_items:
            # Validate it's a class (should always be true due to @injectable validation)
            if not isinstance(item, type):
                logger.warning(
                    f"Skipping non-class decorated item: {item}. "
                    f"Only classes can be registered by name."
                )
                continue

            name = item.__name__
            try:
                component_name_registry.register(name, item)
            except TypeError as e:
                # ComponentNameRegistry validation failed
                logger.warning(f"Failed to register {name}: {e}")
                continue
```

**Rationale:**
- Double-check that scanned items are classes
- ComponentNameRegistry.register() will validate again (defense in depth)
- Log warnings for any non-class items (shouldn't happen with @injectable)

#### 5.5 Update All Type Hints in Tests

**Files:**
- `tests/services/test_component_lookup.py`
- `tests/test_component_lookup_integration.py`
- All other test files

**Changes:**
```python
# BEFORE
def Button(**kwargs):
    """Function component."""
    return "<button>Click</button>"

registry.register("Button", Button)  # Should fail now

# AFTER
@dataclass
class Button:
    """Class component."""
    label: str = "Click"

registry.register("Button", Button)  # Correct

# BEFORE (in tests that verify error handling)
def test_register_function_component():
    """Test that functions cannot be registered."""
    registry = ComponentNameRegistry()

    def my_function():
        return "hello"

    # This should now raise TypeError at registration time
    with pytest.raises(TypeError, match="only accepts class types"):
        registry.register("MyFunc", my_function)
```

#### 5.6 Update Type Hints in Examples

**Files:**
- All example files in `examples/*/components/*.py`
- All example files in `examples/*/services/*.py`

**Changes:**
- Ensure all components are classes (already should be)
- Remove any function components from examples (except KeywordInjector educational example)
- Add type hints to component methods
- Ensure proper return type annotations

#### 5.7 Add Type Checking to CI/CD

**File:** `.github/workflows/test.yml` (if exists) or create new config

**Changes:**
```yaml
- name: Type check with mypy
  run: |
    pip install mypy
    mypy src/tdom_svcs --strict
```

**OR** add to `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.14"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## Summary of Type Hinting Solution

### What Changes

1. **ComponentNameRegistry** - Only accepts `type` (classes), validates at registration
2. **ComponentLookup** - Uses `type[T]` generic parameter, eliminates casts
3. **scan_components()** - Validates scanned items are classes before registration
4. **All tests** - Updated to use class components, test function rejection
5. **All examples** - Ensure proper type hints (already should be correct)
6. **CI/CD** - Add mypy type checking (optional but recommended)

### Benefits

✅ **Type checker happy** - Understands `type[T]` vs `type`
✅ **Fail fast** - Validation at registration time, not lookup time
✅ **Clear errors** - "Only accepts class types" instead of mysterious cast errors
✅ **Policy enforcement** - Impossible to register functions by name
✅ **Better IDE support** - Autocomplete knows exact types
✅ **No more casts** - Use proper generics instead of type assertions

### Breaking Changes

⚠️ **ComponentNameRegistry.register()** now raises `TypeError` for non-class types
- This enforces the class-only policy
- Existing code registering functions will fail (which is correct behavior)
- Add validation where calling register() to handle this

⚠️ **Return type changes** - `ComponentLookup` methods return generic `T` instead of `Callable`
- More precise types
- Should not break existing code (more specific is compatible)

### Testing Strategy

1. **Add tests for TypeError on function registration**
2. **Run mypy on entire codebase** - Should pass with no errors
3. **Verify all existing tests still pass** - Type changes shouldn't break behavior
4. **Test examples with type checker** - Ensure they type check correctly

## Files Requiring Type Hint Updates

### Core Code (Critical)
1. `src/tdom_svcs/services/component_registry/component_name_registry.py` - Remove Callable, add validation
2. `src/tdom_svcs/services/component_registry/models.py` - Update protocol docstrings
3. `src/tdom_svcs/services/component_lookup/component_lookup.py` - Use type[T], remove casts
4. `src/tdom_svcs/scanning.py` - Add validation for class types

### Tests (Update to match)
5. `tests/services/test_component_lookup.py` - Add function rejection tests
6. `tests/test_component_lookup_integration.py` - Ensure using classes
7. `tests/test_scan_components.py` - Ensure using classes
8. All other test files using ComponentNameRegistry

### Examples (Verify correctness)
9. All example files - Should already be correct (using classes)
10. Add one example showing function rejection with clear error

### Documentation
11. Update all specs mentioning ComponentNameRegistry to note class-only
12. Update .claude/instructions.md with type hinting guidelines
13. Update FUNCTION_VS_CLASS_COMPONENTS_PLAN.md with Phase 5

### Configuration (Optional but recommended)
14. `pyproject.toml` - Add mypy configuration
15. `.github/workflows/` - Add mypy to CI/CD

## Verification Checklist - Phase 5

- [ ] ComponentNameRegistry only accepts `type` (not `type | Callable`)
- [ ] ComponentNameRegistry.register() validates isinstance(component_type, type)
- [ ] ComponentNameRegistry.register() raises TypeError with clear message for functions
- [ ] ComponentLookup uses `type[T]` in helper method signatures
- [ ] ComponentLookup eliminates all `cast()` calls (use isinstance() validation instead)
- [ ] scan_components() validates scanned items are classes
- [ ] Test added: function rejection in ComponentNameRegistry.register()
- [ ] Test added: function rejection in scan_components()
- [ ] All existing tests pass with new type validation
- [ ] mypy runs on codebase with --strict mode (optional but recommended)
- [ ] No type checker errors for `Expected type[T], got type`
- [ ] All examples type-check correctly
- [ ] Documentation updated to reflect class-only policy enforcement

---

# FINAL SUMMARY: Complete Implementation Plan

## All Phases Overview

### **Phase 5: Type Hinting Fixes** (HIGHEST PRIORITY - Do First)
**Goal:** Fix recurring `Expected type[T], got type` errors once and for all

**Key Changes:**
- Remove `Callable` from ComponentNameRegistry (class-only)
- Add validation: `isinstance(component_type, type)` at registration
- Use `type[T]` generics in ComponentLookup helpers
- Eliminate all `cast()` calls, use proper TypeVars
- Validate in scan_components() before registration

**Files:** 4 core + 4 tests + examples + docs = ~14 files

**Impact:** Solves root cause, makes all other phases easier

---

### **Phase 0: Injector Updates** (SECOND PRIORITY - Do Second)
**Goal:** Replace KeywordInjector with HopscotchInjector throughout project

**Key Changes:**
- ComponentLookup uses HopscotchInjector (not KeywordInjector)
- All examples use HopscotchInjector for class components
- All tests use HopscotchInjector for class components
- Mission/roadmap clarify injector usage
- One simple function example with KeywordInjector (educational)

**Files:** 2 product docs + 5 specs + 4 core + 4 examples + 4 tests + standards = ~22 files

**Impact:** Enables resource/location-based resolution, production-ready

---

### **Phase 1: Component Type Policy in Specs**
**Goal:** Clarify class vs function component policy in documentation

**Key Changes:**
- Update specs to state class-only for name registration
- Update specs to state Inject[] works for both
- Add policy sections to spec documents
- Create examples showing both patterns

**Files:** 4 spec documents + 1 example = ~5 files

**Impact:** Clear documentation of policy

---

### **Phase 2: Code Validation (if register_component exists)**
**Goal:** Add runtime validation for component types

**Key Changes:**
- Add validation to register_component function
- Update ComponentNameRegistry documentation
- Update protocol documentation
- Add comments to ComponentLookup

**Files:** 3 code files

**Impact:** Runtime enforcement of policy

---

### **Phase 3: Tests and Examples**
**Goal:** Add comprehensive tests and examples

**Key Changes:**
- Test function rejection in register_component
- Test function with Inject[] (direct call, no ComponentLookup)
- Example showing function pattern
- Example showing class pattern

**Files:** 2 test files + 1 example = 3 files

**Impact:** Verify policy enforcement, educate users

---

### **Phase 4: Related Specs and Roadmap**
**Goal:** Update all related documentation

**Key Changes:**
- Check middleware spec for clarity
- Update roadmap items
- Ensure consistency across all specs

**Files:** 2 spec documents

**Impact:** Complete consistency

---

## Total Files Affected

**46 files** across all phases:
- **Phase 5:** 14 files (type system)
- **Phase 0:** 22 files (injector)
- **Phase 1:** 5 files (spec updates)
- **Phase 2:** 3 files (code validation)
- **Phase 3:** 3 files (tests/examples)
- **Phase 4:** 2 files (related docs)
- **New files:** `.claude/instructions.md`, examples, tests

## Recommended Execution Order

1. ✅ **Read and approve this plan** (you are here)
2. 🔥 **Execute Phase 5** (type hinting) - Fixes root cause
3. 🔥 **Execute Phase 0** (injector) - Enables production features
4. 📝 **Execute Phase 1** (specs) - Clarifies policy
5. 💻 **Execute Phase 2** (code validation) - Enforces policy
6. ✅ **Execute Phase 3** (tests) - Verifies policy
7. 📚 **Execute Phase 4** (docs) - Completes consistency

## Success Criteria

After completing all phases:

✅ No type errors (`Expected type[T], got type`)
✅ ComponentNameRegistry enforces class-only at registration
✅ ComponentLookup uses HopscotchInjector
✅ All examples use correct injector
✅ All tests pass with strict type checking
✅ Documentation is clear and consistent
✅ Policy enforced at multiple levels (type system, runtime, documentation)
✅ Users cannot accidentally register functions by name
✅ Type checker provides helpful autocomplete and error messages
