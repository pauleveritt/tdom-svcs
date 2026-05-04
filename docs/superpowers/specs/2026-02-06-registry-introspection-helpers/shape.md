# Registry Introspection Helpers — Shape

## Problem

Users need a way to inspect what components and middleware are registered in a HopscotchRegistry at runtime. This is essential for:
- Debugging registration issues
- Building admin interfaces
- Generating documentation
- Understanding application structure

## Appetite

Small batch (1-2 hours). This is a focused enhancement to expose existing registry state through clean APIs.

## Solution

Two introspection functions:
- `list_components()` — Returns all registered component services grouped by type
- `list_middlewares()` — Returns all registered middleware types with priorities

Return types are frozen dataclasses for immutability and clarity.

## Scope

### In Scope
- Introspection of component registrations (single and multiple variations)
- Introspection of middleware registrations
- Frozen dataclass return types
- Public API exposure
- Tests and documentation

### Out of Scope
- Modifying registry state (read-only)
- Introspection of individual container state
- Performance optimization for large registries
- CLI tools for inspection

## Design Decisions

### Return Types
Use frozen dataclasses instead of dicts or tuples for:
- Type safety
- IDE autocomplete
- Clear attribute names
- Immutability guarantees

### Data Structure
For components:
- Return `dict[type, ComponentInfo]` — easy lookup by service type
- Each `ComponentInfo` has a tuple of variations

For middleware:
- Return `tuple[MiddlewareInfo, ...]` — ordered list
- Include priority information for each middleware

### Implementation Strategy
- Access private `_single_registrations` and `_multi_registrations` from ServiceLocator
- Extract metadata from `FactoryRegistration` objects
- Reuse existing `get_middleware_types()` for middleware introspection

## Rabbit Holes
- Don't try to introspect container-specific overrides
- Don't worry about performance optimization yet
- Don't add mutation capabilities (keep it read-only)

## No-Gos
- No write operations
- No container-level introspection (registry-level only)
- No backwards compatibility shims
