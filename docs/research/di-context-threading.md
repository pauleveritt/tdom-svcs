# DI Context Threading: Architecture Analysis

## Problem

tdom-svcs exists to integrate svcs dependency injection with tdom template rendering.
Today this requires subclassing tdom's `ProcessorService` and overriding `_process_component`
-- an 80-line method that mirrors tdom internals. This is fragile: if tdom changes that method,
tdom-svcs breaks silently.

This document analyzes why the subclass exists and what alternatives could replace it.

## svcs Registry/Container Boundaries

svcs defines two clear scoping boundaries:

- **Registry** -- system-wide, created at startup, holds factories and type mappings.
  Lives as long as the application process.
- **Container** -- per-request, created for each HTTP request, holds resolved service
  instances. Scoped to one request's lifetime. Destroyed after the response.

HopscotchContainer extends this with two additional per-request dimensions:

- **`resource`** -- per-request context instance (e.g., the current customer/tenant type).
  Used by ServiceLocator for resource-based component resolution.
- **`location`** -- per-request URL path (`PurePath`). Used by ServiceLocator for
  location-based component resolution (e.g., `/fr/` gets French components).

## How tdom-svcs Bridges the Gap

The integration works in three steps:

1. **Entry point**: `html(template, *, context=container)` -- the user passes a
   HopscotchContainer explicitly at the top-level render call.

2. **ContextVar transport**: A module-level `_di_context: ContextVar[object | None]`
   stores the container for the duration of `process_template()`. This is necessary
   because tdom's recursive `_process_tnode` call chain has no parameter for passing
   extra state to component invocations.

3. **Component interception**: `DIProcessorService._process_component()` reads the
   ContextVar and adds four behaviors to tdom's base component invocation:
   - Read context from ContextVar
   - Look up implementation overrides via `_get_implementation()` (ServiceLocator)
   - Thread `context=` to components that declare a `context` parameter
   - Use `HopscotchInjector` to resolve `Inject[T]` fields when the context is a
     DI container

## The Core Tension

The ContextVar is doing double duty:

1. **Transport** -- getting the container through tdom's recursive processing chain
   (a legitimate concern -- tdom's `ProcessorService` has no hook for threading extra
   state through the `_process_tnode` call chain).

2. **DI integration point** -- every component invocation reads it to decide whether
   to inject dependencies.

But `HopscotchContainer` is already a "per-request context" object by design. It
carries resource, location, and resolved services. The only reason we need a ContextVar
at all is that tdom's `ProcessorService._process_component()` has no parameter or hook
for "extra stuff to pass to components."

## Three Approaches

### Approach 1: Hook in tdom (Recommended)

If `ProcessorService` accepted a component interceptor callback -- something like:

```python
type ComponentInterceptor = Callable[
    [type | Callable, dict[str, object], Template],
    tuple[type | Callable, dict[str, object]],
]
```

...that wraps `_process_component` invocation, then tdom-svcs wouldn't need to subclass
at all.

**What changes:**
- tdom adds a `component_interceptor` field to `ProcessorService` (optional, defaults
  to identity). Called before component invocation with `(callable, kwargs, children)`,
  returns `(callable, kwargs)`.
- tdom-svcs provides an interceptor function (~30 lines) that does the four things
  listed above: implementation override, context threading, DI injection, and the
  factory pattern (`__call__` on class component instances).
- The ContextVar becomes an implementation detail of the interceptor, not of the
  processor subclass.

**Benefits:**
- Eliminates the fragile 80-line `_process_component` override entirely
- tdom stays dependency-free
- Other DI frameworks (not just svcs/Hopscotch) could provide their own interceptors
- tdom-svcs shrinks to essentially one function

**Tradeoffs:**
- Requires upstream change to tdom
- Hook API design needs care (what arguments? what return type?)

### Approach 2: Framework-Level ContextVar

Django, Flask, and FastAPI all have per-request ContextVars (Flask's `g`,
Starlette's `request`). If `HopscotchContainer` itself were stored in a ContextVar
by the web framework's request middleware, then any code running during request
processing could resolve services without being passed the container explicitly.

```python
# In framework middleware:
_current_container: ContextVar[HopscotchContainer] = ContextVar("_current_container")

# In a component:
def Greeting(users: Inject[Users]):
    # No context= needed -- container is ambient
    ...
```

**What changes:**
- `html(template)` with no `context=` parameter. The container is always ambient.
- Components with `Inject[T]` are resolved against whatever container is current.
- `context=` disappears from the public API entirely.

**Benefits:**
- Eliminates `context=container` boilerplate at every `html()` call site
- Natural fit for web frameworks that already use ContextVars for request scoping
- Components don't need to know about the container at all

**Tradeoffs:**
- Implicit global state vs explicit parameter passing
- Harder to test (must set up ContextVar in test fixtures)
- Doesn't work for non-web use cases without a ContextVar setup step

### Approach 3: Container as an Injectable

What if the container were resolved through the type system itself? A component
that needs to call `html()` for sub-rendering would declare:

```python
@dataclass
class Body:
    container: Inject[HopscotchContainer]

    def __call__(self) -> str | Markup:
        return html(t"<body><{Greeting} /></body>", context=self.container)
```

The container resolves itself: `container.register_local_value(HopscotchContainer, container)`.

**What changes:**
- No special `context=` parameter threading -- container is just another dependency
- Components that need to sub-render get the container injected like any other service

**Benefits:**
- Unifies "context threading" with "dependency injection" -- one mechanism for everything
- Explicit about which components need the container
- No ContextVar needed for the DI concern (still needed for tdom transport)

**Tradeoffs:**
- Verbose for components that compose other components
- Circular resolution (container resolving itself) is unusual, though svcs supports it
- Still needs the ContextVar for tdom's internal processing chain

## Analysis

Approaches 2 and 3 address the *user API* (how callers pass the container) but don't
address the *implementation* problem (the fragile subclass). Only Approach 1 fixes
the root cause.

Approaches are not mutually exclusive:
- Approach 1 + 2: tdom has a hook, framework middleware sets a ContextVar, tdom-svcs
  interceptor reads it. Clean at every layer.
- Approach 1 + 3: tdom has a hook, container is injectable, interceptor still handles
  the plumbing. Explicit but verbose.

## Recommendation

**Start with Approach 1.** The subclass is the most fragile part of tdom-svcs and the
hook is a clean upstream change that benefits anyone integrating with tdom's component
system. This is independent of how the container reaches the hook (explicit parameter,
ContextVar, or injection).

The `_process_component` override does exactly four extra things vs the base:

1. Read context from ContextVar
2. Look up implementation overrides (`_get_implementation`)
3. Thread `context=` to components that accept it
4. Use `HopscotchInjector` when `Inject[T]` fields are present

A single `before_invoke_component(callable, kwargs, children) -> (callable, kwargs)` hook
in tdom would let tdom-svcs do all four without subclassing.

After the hook exists, Approach 2 (framework-level ContextVar) becomes a natural follow-up
for web framework integrations like tdom-django.

## Current State (April 2026)

- tdom's `ProcessorService` has no component hook
- tdom-svcs subclasses `ProcessorService` with `DIProcessorService`
- The subclass overrides `_process_component` (~80 lines mirroring tdom internals)
- A ContextVar transports the container through the processing chain
- This works but is fragile and couples tdom-svcs to tdom's internal method signatures
