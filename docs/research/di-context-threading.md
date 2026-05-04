# DI Context Threading: Architecture Analysis

## Problem

tdom-svcs exists to integrate svcs dependency injection with tdom template rendering.
The original implementation subclassed tdom's `ProcessorService` and overrode an
80-line `_process_component` method that mirrored tdom internals — fragile, and
silently broken if tdom changed the method.

The current implementation is cleaner: tdom exposes `ComponentProcessor` as a
documented extension point, and `DIComponentProcessor` plugs in via
`TemplateProcessor.component_processor_api`. What remains is a different question:
the module-level globals in `processor.py`.

```python
_di_context: ContextVar[svcs.Container | None] = ContextVar(...)  # line 30
_tp = TemplateProcessor(...)                                       # line 155
_default_ctx = ProcessContext()                                    # line 160
```

This document analyzes how the container reaches the processor, what each global
is doing, and what svcs/Hopscotch's structured lifecycle facilities offer as
alternatives.

## svcs Registry/Container Boundaries

svcs defines two clear scoping boundaries:

- **Registry** — system-wide, created at startup, holds factories and type mappings.
  Lives as long as the application process.
- **Container** — per-request, created for each HTTP request, holds resolved service
  instances. Scoped to one request's lifetime. Destroyed after the response.

HopscotchContainer extends this with two additional per-request dimensions:

- **`resource`** — per-request context instance (e.g., the current customer/tenant type).
  Used by ServiceLocator for resource-based component resolution.
- **`location`** — per-request URL path (`PurePath`). Used by ServiceLocator for
  location-based component resolution (e.g., `/fr/` gets French components).

## How tdom-svcs Bridges the Gap

The integration works in three steps:

1. **Entry point**: `html(template, *, container=container)` — the user passes a
   `HopscotchContainer` (or any `svcs.Container`) explicitly at the top-level
   render call.

2. **ContextVar transport**: `_di_context` stores the container for the duration
   of `html()`. The reasoning was that `ComponentProcessor.process()`'s signature
   doesn't accept a container parameter and tdom's recursive component dispatch
   needs to read it.

3. **Component interception**: `DIComponentProcessor.process()` reads the
   ContextVar and adds three behaviors to tdom's base component processing:
   - Look up implementation overrides via `_get_implementation()` (ServiceLocator)
   - Pre-prep partial kwargs via `_prep_component_kwargs`
   - Use `HopscotchInjector` to resolve `Inject[T]`, `Resource[T]`, and
     `Get[T, Attr]` fields, then delegate to `super().process()` with the
     resolved kwargs as `provided_attrs`

## The Three Module-Level Globals

### `_di_context` (the ContextVar)

**Role:** Threads the container through tdom's recursive component dispatch.

**Required?** No, but **idiomatic**. tdom's own integration tests use exactly
this pattern (`SystemCtx` in `processor_integration_test.py`) for the same
purpose: threading per-request state through a custom `ComponentProcessor` that
augments `provided_attrs`. Ian's own @NOTE acknowledges ContextVar is the
current mechanism but flags that parameter-passing may be a future improvement.

Two valid alternatives:

1. **Container as a field on `DIComponentProcessor`** (Approach 1 below). Cleaner
   structurally — no spooky action at a distance — but creates a fresh processor
   instance per `html()` call. Diverges from tdom's reference pattern.
2. **Keep the ContextVar** (status quo). Stays aligned with tdom's integration
   test idiom. The "global mutable" critique is real but symmetric — Ian's
   reference code has the same shape.

```python
# Approach 1: container as field
@dataclass(frozen=True)
class DIComponentProcessor(ComponentProcessor):
    container: svcs.Container | None = None

    def process(self, ...):
        if self.container is None:
            return super().process(...)
        # ... use self.container directly
```

The choice between these is a tradeoff between structural cleanliness and
alignment with upstream conventions. See the Approaches section below.

### `_tp` (the configured TemplateProcessor)

**Role:** Module-level singleton holding the configured `TemplateProcessor`
(`slash_void=True`, `uppercase_doctype=True`) wrapping `DIComponentProcessor`.

**Required?** No. `TemplateProcessor` is a cheap frozen dataclass — per-call
construction has negligible overhead.

Two paths to eliminate it:

- **Per-call construction** inside `html()`. Zero state at module level.
- **Registry-as-source-of-truth**: register `TemplateProcessor` as a value service
  and resolve it from the container. Lets users override the configuration via
  registry registration. The Hopscotch scanner (`@injectable` + `scan()`) can wire
  this without any import-time globals.

### `_default_ctx` (the ProcessContext seed)

**Role:** Fresh empty `ProcessContext` passed as `assume_ctx` for the top-level
`html()` call.

**Required?** No. `ProcessContext()` is cheap to construct. Inline it. Or, following
Ian's pattern in tdom's own test suite (see below), expose `assume_ctx` as an
explicit `html()` parameter so callers can override the initial context.

## Comparison: tdom's Own Patterns

Two test files in the upstream tdom project demonstrate complementary patterns.

### Pattern A: `processor_test.py` (basic usage)

The tdom project's `processor_test.py` uses an `html()` helper that mirrors what
tdom-svcs does — minus the DI:

```python
processor_api = _make_default_template_processor(parser_api=TemplateParserProxy())

def html(template: Template, assume_ctx: ProcessContext | None = None) -> str:
    if assume_ctx is None:
        assume_ctx = _default_process_ctx
    return processor_api.process(template, assume_ctx=assume_ctx, app_state=None)
```

| tdom-svcs `processor.py`    | tdom `processor_test.py`     | Role                            |
|-----------------------------|------------------------------|---------------------------------|
| `_tp`                       | `processor_api`              | Configured TemplateProcessor    |
| `_default_ctx`              | `_default_process_ctx`       | Fresh ProcessContext seed       |
| `_di_context` (ContextVar)  | *(none)*                     | DI-specific; not in plain tdom  |

In Pattern A, `assume_ctx` is passed explicitly. The two globals (configured
processor and default context) are baseline tdom idiom.

### Pattern B: `processor_integration_test.py` (request-scoped state)

The integration test file demonstrates **three** mechanisms for threading
per-request state through component processing — and crucially, two of them use
module-level `ContextVar`:

```python
SystemCtx: ContextVar[SystemState | None] = ContextVar("SystemCtx", default=None)

class SystemComponentProcessor(IComponentProcessor[T]):
    default_component_processor_api: IComponentProcessor[T] = ...

    def process(self, ..., provided_attrs=()):
        system_ctx = SystemCtx.get()
        if system_ctx is not None and isclass(component_callable) ...:
            # Protocol → concrete implementation lookup
            component_callable = system_ctx.components[component_callable]
        if system_ctx is not None:
            provided_attrs = provided_attrs + (("request", system_ctx.request),)
        return self.default_component_processor_api.process(...)
```

This is **structurally identical** to `DIComponentProcessor`:
- Reads a module-level `ContextVar` for per-request state
- Looks up implementation overrides (protocol → concrete) — equivalent to our
  `_get_implementation()` (ServiceLocator) lookup
- Augments `provided_attrs` from the contextual state — equivalent to our
  `HopscotchInjector` resolution
- Delegates to `super().process()` (via composition rather than inheritance)

Ian's own comment at the read site (lines 117–120):

> *"This is using the contextvars.ContextVar to get this information but maybe in
> the future we'd have a way to get ctx directly from a parameter."*

So ContextVar is **endorsed but not eternal** — Ian is using it as the current
mechanism while leaving room for an evolution toward parameter passing.

The integration tests also show three other approaches:
- **Callback closure capture** (`AppLoggedInCtx`): a component callback reads a
  ContextVar at render time
- **Untyped `app_state`** (`DictAppState`): a custom processor pulls keys out of
  `app_state` and adds them to `provided_attrs`
- **Typed `app_state`** (`AppState` dataclass): same, with a domain type

So `app_state` is the *officially supported alternative* to ContextVar for
per-request data — but it's a single value that the user typically owns, which is
why tdom-svcs reserves it for user-defined state.

### What's at Module Level in Ian's Integration Tests

Critically, even in `processor_integration_test.py`:

```python
def _make_html(self) -> Callable[[Template], str]:
    tp = TemplateProcessor(component_processor_api=self.SystemComponentProcessor())
    assume_ctx = ProcessContext()

    def _html(t: Template) -> str:
        return tp.process(t, assume_ctx=assume_ctx, app_state=None)
    return _html
```

The `TemplateProcessor` and `ProcessContext` are **closure-captured per session**,
not module-level. Only the `ContextVar` is module-level (and only because
ContextVars must be).

### Bottom Line

| Pattern          | Module-level globals                  | Per-call/session         |
|------------------|---------------------------------------|--------------------------|
| `processor_test.py` (Pattern A)       | `processor_api`, `_default_process_ctx` | `assume_ctx` parameter    |
| `processor_integration_test.py` (Pattern B) | `SystemCtx`, `AppLoggedInCtx`         | `tp`, `assume_ctx`        |
| **tdom-svcs current**                | `_di_context`, **`_tp`**, **`_default_ctx`** | nothing                   |

Two key takeaways:

1. **`_di_context` is idiomatic** per Pattern B. The "spooky action at distance"
   critique applies equally to Ian's reference pattern, and his @NOTE
   acknowledges this is the current state of the art. (See "Tradeoff Deep Dive"
   below for why we chose to diverge anyway.)
2. **`_tp` and `_default_ctx` are out of step.** Neither tdom test pattern keeps
   the configured processor or the default context at module level. Both
   construct them per session/closure. **Eliminating these two is purely an
   alignment with tdom's own conventions.**

## Approaches for Reaching the Container Without a ContextVar

### Approach 1: Container as a Field on DIComponentProcessor (CHOSEN — pair with Approach 2)

```python
def html(template, *, container=None):
    return TemplateProcessor(
        component_processor_api=DIComponentProcessor(container=container),
        slash_void=True, uppercase_doctype=True,
    ).process(template, ProcessContext(), app_state=None)
```

**Eliminates:** `_di_context`, `_tp`, `_default_ctx` — all three.

**Benefits:**
- Single locus of state: each `html()` call has its own processor with its own container
- No module-level mutables at all
- Mirrors tdom's own pattern (just with a configurable processor per call instead
  of a global one)
- Trivial to test: each call is isolated

**Tradeoffs:**
- Two object allocations per `html()` call (`TemplateProcessor` +
  `DIComponentProcessor`). Both are frozen dataclasses; cost is negligible compared
  to template processing itself.

### Approach 2: Register TemplateProcessor on the Registry (CHOSEN — pair with Approach 1)

When a container is provided, resolve `TemplateProcessor` from it:

```python
registry.register_value(TemplateProcessor, TemplateProcessor(
    component_processor_api=DIComponentProcessor(container=...),
    slash_void=True, uppercase_doctype=True,
))

def html(template, *, container=None):
    if container is None:
        return tdom.html(template)  # plain path, no DI
    tp = container.get(TemplateProcessor)
    return tp.process(template, ProcessContext(), app_state=None)
```

The Hopscotch scanner can register this via a setup function discovered by
`scan()`, so applications wire it up declaratively rather than at import time:

```python
def svcs_container(container):
    # called for each new HopscotchContainer
    container.register_local_value(
        TemplateProcessor,
        TemplateProcessor(
            component_processor_api=DIComponentProcessor(container=container),
            slash_void=True, uppercase_doctype=True,
        ),
    )
```

**Eliminates:** `_di_context`, `_tp` (becomes a registered value), `_default_ctx`
(constructed per call).

**Benefits:**
- Configuration lives in the registry — single source of truth, overridable per-app
- Late binding: no import-time globals; the scanner discovers setup functions at
  app-init time
- Aligns with svcs's intended design (lifecycle objects in the registry/container)
- Supports per-application customization (e.g., different `slash_void` or
  `uppercase_doctype` settings)

**Tradeoffs:**
- More complex than Approach 1
- Chicken-and-egg when `container=None`: requires either a fallback (delegate to
  plain `tdom.html()`) or making `container` mandatory
- Container registers itself (Hopscotch already does this for Resource/Location,
  so the pattern is established)

### Approach 3: Framework-Level Ambient Container

For web framework integrations (e.g., a future `tdom-django`), the container can
be set into a ContextVar by request middleware, and `html()` reads it ambient:

```python
def html(template):
    container = _ambient_container.get()
    return TemplateProcessor(
        component_processor_api=DIComponentProcessor(container=container),
        slash_void=True, uppercase_doctype=True,
    ).process(template, ProcessContext(), app_state=None)
```

**Eliminates:** `_tp`, `_default_ctx` from this module. The ContextVar moves to
the framework's request scope (where it logically belongs — alongside Flask's
`g`, Starlette's request scope, etc.).

**Benefits:**
- Eliminates `container=` boilerplate at every `html()` call site
- Natural fit for web frameworks already using ContextVars for request scoping
- Components don't need to know about the container at all

**Tradeoffs:**
- Implicit global state vs explicit parameter
- Doesn't help non-web use cases without a setup step
- Tests must set up the ContextVar in fixtures

### Approach 4: Container as an Injectable

Components that need to call `html()` for sub-rendering can declare the container
as a dependency:

```python
@dataclass
class Body:
    container: Inject[HopscotchContainer]

    def __call__(self) -> str | Markup:
        return html(t"<body><{Greeting} /></body>", container=self.container)
```

**Benefits:**
- Unifies "context threading" with "dependency injection" — one mechanism for everything
- Explicit about which components need the container

**Tradeoffs:**
- Verbose for components that compose other components
- Not a substitute for the other approaches; it's complementary to them

## Tradeoff Deep Dive: Option A vs Option B

### What we're actually deciding

Both options solve the transport problem. Both produce identical observable
behavior. The difference is **where state lives** and **what that costs in
second-order effects**.

### Option A: Keep `_di_context` — pros and cons

**Real pros (not aesthetic):**

- **Async correctness for free.** `ContextVar` values are per-task in asyncio.
  Concurrent async `html()` calls have isolated containers automatically. Option
  B works too, but only because each call gets its own processor; the property
  is unstated.
- **Re-entrancy is handled by the runtime.** A component renders, calls `html()`
  for a subtree with a different container, the parent container is restored on
  `reset()`. Standard pattern; `try/finally` already in place.
- **The processor stays "shape," not "data."** Same instance handles N requests
  — separation between rendering logic and per-request payload. This is what
  Ian preserves in `SystemComponentProcessor`.
- **Allocation budget.** At 10K req/sec × 100 components = 1M `html()` calls/sec;
  three frozen dataclass allocations × 1M = ~1.5ms of CPU/sec just for
  processor instantiation. Not catastrophic, but not free.

**Real cons (not just "spooky"):**

- **Hidden coupling.** `html()` and `DIComponentProcessor` link through a
  module-level name. A reader has to grep for `_di_context.get()` to understand
  how the container reaches the processor. No signature reveals it.
- **Test boilerplate.** Every fixture needs `_di_context.set/reset` plumbing or
  must call through `html()`. With Option B, you construct the processor with
  the container and call `.process()` directly.
- **Process-wide state at import time.** The `ContextVar` object exists at
  module load. Trivial cost but a real fact about the module.

### Option B: Container as a field — pros and cons

**Real pros:**

- **Visible dependencies.** `DIComponentProcessor(container=c)` is what it says.
  No grep required.
- **Trivially testable.** `DIComponentProcessor(container=fake).process(...)` —
  no fixtures, no resets. Saves a few lines per test, multiplied across many
  tests.
- **No ambient state.** Nothing about the process changes when `html()` is
  called. Each invocation is self-contained.

**Real cons (previously underweighted):**

- **Allocation cost is real.** Frozen dataclass instantiation is ~500ns; three
  per call adds up at high QPS. Mitigatable by combining with Approach 2
  (register `TemplateProcessor` per-container, reuse across `html()` calls).
- **Frozen dataclass + mutable Container field is conceptually awkward.**
  `frozen=True` implies value semantics, but `Container` is mutable. Equality
  and hashing fall back to identity for the container — fine, but inconsistent
  with the frozen intent.
- **Divergence from upstream pattern.** Future contributors reading both
  codebases see inconsistency. Migration cost if tdom adopts parameter-passing
  per Ian's @NOTE is small either way (~10 LOC).
- **Re-entrancy works for a different reason.** With ContextVar, the runtime
  handles it. With per-call construction, each call has its own processor.
  Both correct, but the mechanism is implicit in B.

### Hidden symmetry

Both options expose the same surface to:
- Container mutation during processing
- The `container=None` no-DI path (None checks needed in both)
- Resource/Location threading
- Migration cost if tdom adds parameter passing (~10 LOC either way)

Neither option is meaningfully more or less robust to misuse.

### What tips the decision

The case is closer than first analysis suggested. The "global mutable" objection
that motivates B applies equally to Ian's `SystemCtx` — and Ian shipped it. So
B isn't obviously cleaner on aesthetic grounds.

What tips the decision: **structural alignment with the rest of this codebase.**
tdom-svcs is built on svcs/Hopscotch, where the registry/container is the
canonical lifecycle holder. If the project's whole premise is "lifecycle data
lives in svcs," then having a private module-level `ContextVar` outside that
system is incongruous. Option B paired with Approach 2 (registering
`TemplateProcessor` on the container) lets the entire processor lifecycle
become a svcs concern — *the same way every other lifecycle-bound object in
the codebase is managed*.

The "alignment with upstream" argument for Option A is real but weaker, because
it's alignment with a *test pattern*, not a public API contract. tdom's public
extension point (`ComponentProcessor`) places no constraint on how subclasses
hold per-render state.

## Decision: Option B + svcs as source of truth

The chosen end-state:

1. **`DIComponentProcessor` carries `container` as a frozen field** (Option B).
   No more `_di_context` ContextVar.

2. **`TemplateProcessor` is registered as a local value on each container**,
   with `component_processor_api` pre-wired to
   `DIComponentProcessor(container=container)` for that container (Approach 2).
   The Hopscotch scanner discovers this via a `svcs_container` setup function:

   ```python
   def svcs_container(container):
       container.register_local_value(
           TemplateProcessor,
           TemplateProcessor(
               component_processor_api=DIComponentProcessor(container=container),
               slash_void=True,
               uppercase_doctype=True,
           ),
       )
   ```

3. **`html()` resolves `TemplateProcessor` from the container** and processes
   the template:

   ```python
   def html(template, *, container=None):
       if container is None:
           return tdom.html(template)  # plain path, no DI
       tp = container.get(TemplateProcessor)
       return tp.process(template, ProcessContext(), app_state=None)
   ```

**Result:**

- Zero module-level mutable state in `processor.py`. `_di_context`, `_tp`, and
  `_default_ctx` are all gone.
- All processor lifecycle is managed by svcs. The container *is* the source of
  truth for the rendering pipeline.
- Allocation cost mitigated: `TemplateProcessor` is constructed once per
  container (at container init), not per `html()` call. Each `html()` call
  reuses the registered processor.
- Customization path: applications that want a different `TemplateProcessor`
  configuration (e.g., different `slash_void`/`uppercase_doctype` settings)
  override it via their own `svcs_container` setup function, or by registering
  a different `TemplateProcessor` value before calling `html()`.

**Approaches 3 and 4 are still available as future layering** (framework-ambient
container, container-as-injectable for sub-rendering), but neither is part of
the core commitment.

## Current State (April 2026) — Implemented

Items 32–34 from the roadmap are complete. `processor.py` now has zero
module-level mutable state.

**What changed:**

- `DIComponentProcessor` carries `container: svcs.Container | None = None` as
  a frozen field. `_di_context` ContextVar is gone.
- `_tp` and `_default_ctx` module globals are gone.
- `html()` is a thin dispatcher:
  - `container=None` → delegates to `tdom.html(template)`.
  - `container` provided → resolves `TemplateProcessor` from the container
    (registering it lazily on first call via `container.register_local_value`),
    then calls `tp.process(template, ProcessContext(), app_state=None)`.

**Implementation note — lazy registration vs explicit `svcs_container`:**

The roadmap described an explicit `svcs_container` setup function discovered
by `scan()`. In practice, a self-initialising lazy pattern is cleaner: `html()`
catches `svcs.exceptions.ServiceNotFoundError`, constructs the processor, and
registers it as a local value so the second call reuses it. This avoids
requiring users to scan `tdom_svcs` separately.

The net effect is identical to the design decision: the container is the source
of truth for the `TemplateProcessor`, allocation cost is amortised across calls
on the same container, and no ContextVar exists anywhere in the module.

**Test update:**

One test (`test_component_object_capture_factory`) previously set `_di_context`
manually to inject a custom `RecordingProcessor`. It now passes
`container=container` to `RecordingProcessor(container=container)` at
construction time — simpler and explicit.
