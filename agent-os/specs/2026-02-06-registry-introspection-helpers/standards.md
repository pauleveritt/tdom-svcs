# Registry Introspection Helpers — Standards

## Applicable Standards

### frozen-dataclass-services
All return types are frozen dataclasses for immutability:
- `ComponentVariation` — frozen dataclass
- `ComponentInfo` — frozen dataclass with tuple of variations
- `MiddlewareInfo` — frozen dataclass

### protocol-first-design
Types clearly define the contract:
- Return types are explicit and typed
- Function signatures use type hints
- No `Any` in public API (only for registry parameter)

### function-based-tests
Tests are written as functions, not classes:
- `test_list_components_empty_registry()`
- `test_list_components_single_registration()`
- `test_list_middlewares_empty_registry()`
- etc.

### sybil-doctest
Doctests in docstrings will be tested:
- Add usage examples to function docstrings
- Examples show actual output structure
- Sybil will automatically test these

## Implementation Patterns

### Frozen Dataclasses
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ComponentVariation:
    """Single component implementation variation."""
    implementation: type
    resource: type | None
    location: PurePath | None
```

### Type Hints
```python
def list_components(registry: Any) -> dict[type, ComponentInfo]:
    """List all registered component services."""
    ...
```

### Doctest Examples
```python
def list_components(registry: Any) -> dict[type, ComponentInfo]:
    """List all registered component services.

    >>> registry = HopscotchRegistry()
    >>> @registry.component()
    ... class Greeter:
    ...     pass
    >>> result = list_components(registry)
    >>> Greeter in result
    True
    """
    ...
```

## Quality Gates

1. All tests pass
2. Type checking passes (ty)
3. Linting passes (ruff)
4. Doctests pass (via sybil)
5. All return types are frozen dataclasses
