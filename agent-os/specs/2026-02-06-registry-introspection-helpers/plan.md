# Registry Introspection Helpers — Implementation Plan

## Summary

Create `list_components()` and `list_middlewares()` helper functions for inspecting registered items in a HopscotchRegistry. This enables runtime inspection and debugging of registry state.

---

## Task 1: Save Spec Documentation

Create `agent-os/specs/2026-02-06-registry-introspection-helpers/` with:

- **plan.md** — This full plan
- **shape.md** — Shaping notes (scope, decisions, context)
- **standards.md** — Relevant standards (frozen-dataclass-services, protocol-first-design, function-based-tests, sybil-doctest)
- **references.md** — Pointers to reference implementations

---

## Task 2: Create Introspection Module with Types

Create `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/introspection.py` with:

### Frozen Dataclass Types

```python
@dataclass(frozen=True)
class ComponentVariation:
    """Single component implementation variation."""
    implementation: type
    resource: type | None
    location: PurePath | None

@dataclass(frozen=True)
class ComponentInfo:
    """Complete info about a registered component service type."""
    service_type: type
    variations: tuple[ComponentVariation, ...]

@dataclass(frozen=True)
class MiddlewareInfo:
    """Info about a registered global middleware type."""
    middleware_type: type[AnyMiddleware]
    priority: int | None
```

---

## Task 3: Implement `list_components()`

```python
def list_components(registry: Any) -> dict[type, ComponentInfo]:
```

**Logic:**
1. Access `registry.locator` (ServiceLocator)
2. Iterate `locator._single_registrations` (single variations)
3. Iterate `locator._multi_registrations` (multiple variations)
4. For each `FactoryRegistration`, create `ComponentVariation`
5. Group by `service_type`, return `dict[type, ComponentInfo]`

**Key files to reference:**
- `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/locator.py` — ServiceLocator, FactoryRegistration

---

## Task 4: Implement `list_middlewares()`

```python
def list_middlewares(registry: Any) -> tuple[MiddlewareInfo, ...]:
```

**Logic:**
1. Reuse existing `get_middleware_types(registry)` from `tdom_svcs.middleware`
2. For each middleware type, extract default priority from dataclass field
3. Return tuple of `MiddlewareInfo`

**Key files to reference:**
- `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/middleware.py:107` — `get_middleware_types()`

---

## Task 5: Update Package Exports

Update `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/__init__.py`:

Add imports:
```python
from tdom_svcs.introspection import (
    ComponentInfo,
    ComponentVariation,
    MiddlewareInfo,
    list_components,
    list_middlewares,
)
```

Add to `__all__`:
```python
"ComponentInfo",
"ComponentVariation",
"MiddlewareInfo",
"list_components",
"list_middlewares",
```

---

## Task 6: Write Tests

Create `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_introspection.py`:

**Test cases for `list_components`:**
- Empty registry returns empty dict
- Single registration returns correct ComponentInfo
- Multiple variations for same service type
- Returns frozen dataclasses (immutable)

**Test cases for `list_middlewares`:**
- Empty registry returns empty tuple
- Single middleware with priority extraction
- Multiple middlewares
- Returns frozen dataclasses (immutable)

---

## Task 7: Add Documentation

Create `/Users/pauleveritt/projects/t-strings/tdom-svcs/docs/services/introspection.md`:

- Module overview with examples
- API documentation for each function/type
- Use cases: debugging, admin interfaces, documentation generation

---

## Task 8: Update Roadmap

Mark item 15 as complete in `/Users/pauleveritt/projects/t-strings/tdom-svcs/agent-os/product/roadmap.md`

---

## Verification

1. **Run tests**: `just test tests/test_introspection.py`
2. **Run all tests**: `just test`
3. **Type check**: `just ty`
4. **Lint**: `just lint`
5. **Manual verification**: Create a registry with components and middleware, call both functions, verify output structure

---

## Standards Applied

- **frozen-dataclass-services** — All return types are frozen dataclasses
- **function-based-tests** — Tests as functions, not classes
- **sybil-doctest** — Doctests in docstrings will be tested
- **protocol-first-design** — Types define the contract clearly
