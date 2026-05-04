# Port tdom-svcs to `tstring-html` `ian/integrations`

*Date: 2026-04-26*

## Problem

Today, `tdom-svcs/src/tdom_svcs/processor.py` is a "monkeypatch fork" of tstring-html.
It subclasses `ProcessorService` and re-implements `_process_component` end-to-end
(~150 lines) to add three concerns: container threading, `Inject[T]` field resolution,
and Protocol → impl override. It also pre-renders children to `Markup`, allows
components to return `str | Markup`, and accepts arbitrary `context: object | None`
including dicts.

Upstream's `ian/integrations` branch introduces a clean extension point:
`IComponentProcessor[T]` with a single `process()` method. The default
`ComponentProcessor` does the bookkeeping; subclasses can swap inputs and delegate.
The generic `app_state: T` is threaded through every recursive call — this is the
natural slot for the DI container.

We want to retire the fork in favor of a thin DI subclass on the new API.

## Decisions (locked-in)

These are settled before planning:

1. **`app_state` IS the `svcs.Container`** (or `None`). No dict path. No arbitrary
   context. tdom-svcs parameterizes `TemplateProcessor[svcs.Container | None]`.
2. **`None` remains valid** for `context`/`app_state`. Three production sites in
   themester call `html(template)` with no container (layout parsing, CLI, test
   scaffolding). The container is per-request-render only.
3. **Components return `Template`, not `str | Markup`.** Aligns with new upstream
   contract. Eliminates manual `html()` recursion inside components, manual
   `context=` threading, and `Markup(children)` wrapping.
4. **`children` is a `Template`**, not a pre-rendered `Markup`. Components embed it
   via `t"...{children}..."`; the processor recurses naturally.
5. **`@middleware` / `@hookable` are deferred.** Plumbing exists in tdom-svcs but is
   unused outside its own examples. Preserve as-is; defer integration work until
   there's a real consumer.
6. **No external consumers exist.** Free to make breaking changes without compat
   shims or deprecation windows.

## Workspace findings

### Consumers of `tdom_svcs`

- **themester** — the only real consumer. 3 production imports (`testing/sphinx.py`,
  `layouts/models.py`, `cli/layout_generate.py`) + dozens of examples and tests.
  Uses `Resource[T]` and `location`-based impl override (via `app.request_container(
  request, resource=resource)` in `examples/container/container_lifecycle.py:88`).
- **tdom-assets** — does not import `tdom_svcs`. svcs-native: registers
  `AssetCollector` via `@injectable`, container scope = request scope. Per-request
  state is achieved by container lifecycle alone (`tests/test_services.py:45-56`).
  Components that mutate the collector during render need only:
  (a) container threads to `Inject[T]`-using components,
  (b) same container instance is accessible to the caller after `html()` returns.
  Both are preserved by the port.
- **tdom-layout, storyville** — do not import `tdom_svcs`.

### Patterns that the port removes

- Manual `def __call__(self, context=None) -> str` signature, with internal
  `html(t"...", context=context)` calls. Becomes `def __call__(self) -> Template`
  returning `t"..."` directly.
- `<main>{Markup(self.children)}</main>` — becomes `<main>{children}</main>`,
  where `children: Template`.
- `Layout(children=body_node)(context=context)` construction-and-call patterns —
  becomes `t"<{Layout} children={body_node} />"` (template form).
- `_di_context: ContextVar` and ContextVar reset/restore in `tdom_svcs.html()` —
  the new upstream's `app_state` parameter handles this.
- The `dict | object | None` `ContextArg` type alias and `is_di_container`
  TypeGuard.

### Patterns that the port preserves

- `Inject[T]` and `Resource[T]` field resolution via `HopscotchInjector`.
- Protocol → impl resolution via `_get_implementation` reading `container.resource`,
  `container.location`, and `registry.locator.get_implementation`.
- `tdom_svcs.html(template, *, container=None) -> str` as the top-level entry point.
- `scan()`, `list_components()`, `list_middlewares()` introspection helpers.

### Migration scope (themester)

- 7 production sites with `__call__(self) -> str` (in `src/themester/`):
  `cli/layout_generate.py`, `layouts/decorators.py`, `layouts/types.py` (Protocol),
  `views/__init__.py` (Protocol), `views/decorators.py` (×3).
- ~30 example components and ~70 test sites.
- 1 view-system change with real implementation work: `themester/views/__init__.py`
  `get_view()` currently dispatches on whether the view's `__call__` accepts a
  `context` parameter. Once views return `Template`, this branching collapses;
  `get_view` calls `view_instance()` for the Template and pipes through
  `tdom_svcs.html(t, container=container)`.

## Plan

Three stages, each independently mergeable, each with its own quality + test gate.

### Stage 1 — Cleanup against current upstream (~1 day)

Goal: shrink the fork without touching upstream API or workspace contracts.

Scope: `tdom-svcs/src/tdom_svcs/processor.py` and `types.py` only.

Changes:
- `types.py`: remove `DIContainer` Protocol and `is_di_container`. Re-export
  `svcs.Container` if convenient.
- `processor.py`:
  - Drop `ContextArg = object | None` alias. Type as `svcs.Container | None`.
  - Drop the `is_di_container` guards (the type system enforces it).
  - Remove unreachable dict-handling branches.
  - `html()` signature: `html(template, *, container: svcs.Container | None = None) -> str | Markup`.
- Tests: delete `test_html_wrapper.py` parametrizations that pass dict context.
  Update remaining tests to use `container=` keyword.

What stays unchanged: `_process_component` body shape, ContextVar transport,
`str | Markup` return support, children pre-rendering. Those move in Stage 3.

Verify: `just quality && just test` in tdom-svcs and themester. Themester examples
should still run identically.

### Stage 2 — Workspace migration to `Template`-returning components (~2-3 days)

Goal: make every component return `Template` and accept `Template` children, so
Stage 3's port can be a trivial subclass.

Scope: themester (production, examples, tests, docs); tdom-svcs's own
examples and tests.

This stage requires tdom-svcs to support BOTH `Template` and `str | Markup`
component returns simultaneously during the migration window. The current fork
already does — the conditional `match result_t` block in `_process_component`
handles all three.

Sub-steps (each independently committable):
1. **Update Protocol definitions:** `themester/views/decorators.py:View`,
   `themester/layouts/types.py:Layout`. Change `__call__(self) -> str: ...` to
   `__call__(self) -> Template: ...`.
2. **Migrate themester production code:**
   - `themester/cli/layout_generate.py` — return `Template`, wrap with `html()` at
     the outermost call.
   - `themester/layouts/decorators.py`, `views/decorators.py` — update generated
     `__call__` bodies.
   - `themester/views/__init__.py:get_view` — collapse the `context` branching;
     call `view_instance()` for a `Template`, pipe through `tdom_svcs.html(t,
     container=container)` for the final string.
3. **Migrate themester examples** in groups: `basic/`, `layouts/`, `views/`,
   `static_site/`, `request/`, `container/`, `ssg/`. One commit per group.
4. **Migrate themester tests** to match. Many tests assert against rendered HTML
   strings; only the component shapes change.
5. **Migrate themester docs** after the corresponding code is in place.
6. **Migrate tdom-svcs own examples and tests** — `examples/basic/`, `hopscotch/`,
   `middleware/`, `tests/test_*.py`.

Verify after each sub-step: `just quality && just test` in the affected package.
After all sub-steps: full workspace run.

### Stage 3 — Port to `ian/integrations` + workspace branch with hook (~half-day)

Goal: replace the monkeypatch fork with a thin `ComponentProcessor` subclass on
the new upstream API. Apply the proposed `_invoke_component` hook locally in the
workspace's `tstring-html/` member so we don't have to wait for upstream merge.

Pre-requisites:
- Stage 2 complete (all components return `Template`).

Workspace `tstring-html/` setup:
- Branch the workspace's `tstring-html/` off `ian/integrations` to a local
  branch (e.g. `pauleveritt/invoke-component-hook`).
- Apply the hook to `tdom/processor.py:ComponentProcessor` (~6 lines, see
  "Upstream ask" below).
- Run `just quality && just test` in `tstring-html/`. The default behavior
  is unchanged; existing tests pass.
- Open the upstream PR concurrently. Workspace continues on the local branch
  until/unless upstream merges. If upstream merges with changes, rebase or
  squash the local branch onto the merged version.

Pin: keep `tdom = { workspace = true }` in tdom-svcs's `pyproject.toml`. The
workspace branch is the source of truth.

Changes to `tdom-svcs/src/tdom_svcs/processor.py`:

```python
@dataclass(frozen=True)
class DIComponentProcessor(ComponentProcessor[svcs.Container | None]):
    def process(
        self, template, last_ctx, app_state, component_callable,
        attrs, component_template, provided_attrs=(),
    ):
        if app_state is not None and isinstance(component_callable, type):
            component_callable = _get_implementation(app_state, component_callable)
        return super().process(
            template, last_ctx, app_state, component_callable,
            attrs, component_template, provided_attrs,
        )

    def _invoke_component(self, app_state, callable_, kwargs):
        if app_state is not None and needs_dependency_injection(callable_):
            return HopscotchInjector(container=app_state)(callable_, **kwargs)
        return callable_(**kwargs)


_tp = TemplateProcessor[svcs.Container | None](
    component_processor_api=DIComponentProcessor(),
    slash_void=True,
    uppercase_doctype=True,
)


def html(template, *, container=None) -> str:
    return _tp.process(template, assume_ctx=ProcessContext(), app_state=container)
```

Delete:
- `_di_context: ContextVar` and ContextVar transport.
- `extract_embedded_template` import and call.
- `_resolve_t_attrs` import and call.
- The `match result_t` block (factory pattern, str/Markup wrapping) — handled
  upstream now.
- `ComponentResult = Template | str | Markup` type alias.
- Children pre-rendering logic.

Verify: `just quality && just test` in tdom-svcs and themester.

### Stage 4 — Adopt as workspace-wide processor (~half-day to 1 day)

Goal: every HTML rendering path in the workspace goes through `tdom_svcs.html()`,
regardless of whether DI is needed. Unifies the rendering contract on a single,
DI-aware entry point that gracefully no-ops when `container=None`.

Rationale: with the port complete, `tdom_svcs.html(template, container=None)`
behaves identically to `tdom.html(template)` — the `DIComponentProcessor`
override and `_invoke_component` are both no-ops when `app_state is None`. There
is no reason for any workspace member to import `tdom.html` directly. Routing
everything through tdom-svcs means future DI features land for every consumer
without further migration.

Sub-steps:
1. **Audit workspace for direct `tdom.html` / `tdom.svg` imports.** Grep for
   `from tdom import` and `from tdom.processor import` across all workspace
   members.
2. **Switch imports to `from tdom_svcs import html`.** Confirm the call sites
   pass `container=` if they have one, or leave the default `None`.
3. **Verify byte-identical output for `container=None` paths.** Spot-check a
   few rendered fixtures pre- and post-switch.
4. **Decide what to do with `tdom_svcs.svg()`.** If consumers use `tdom.svg`,
   either re-export it from tdom-svcs (with the same `container` parameter) or
   leave the direct import in place. Defer if there are no consumers.
5. **Consider promoting `tdom_svcs.html` to be `the` workspace render entry
   point in workspace docs** (`README.md`, member CLAUDE.md files). Optional
   polish; can defer.

Members to check:
- `themester` — already on `tdom_svcs.html` after Stage 2; verify no leftover
  direct imports.
- `tdom-assets` — does not render HTML (operates on rendered strings via
  selectolax). No changes expected.
- `tdom-layout` — verify; the README didn't show direct `tdom.html` use but
  worth confirming.
- `storyville` — verify; ships its own story renderer that may import
  `tdom.html` directly.
- `tdom-svcs` examples and tests — already use `tdom_svcs.html`, but check for
  any `from tdom import` leakage.
- `tstring-html/examples/` and `tstring-html/sphinx/` — these are upstream
  demos, not workspace consumers. Leave alone.

Verify: full workspace `just ci-checks` pass. Compare a representative SSG
build (themester `examples/ssg/with-layout/` → output dir) byte-for-byte
against a Stage-3 baseline to ensure the import switch is invisible.

## Upstream ask

Before Stage 3 can be a thin subclass, upstream needs one hook on
`ComponentProcessor`:

```python
@dataclass(frozen=True)
class ComponentProcessor[T = DefaultAppState](IComponentProcessor[T]):
    def _invoke_component(
        self,
        app_state: T,
        callable_: Callable[..., object],
        kwargs: dict[str, object],
    ) -> object:
        """Hook for replacing the bare invocation; override to inject DI."""
        return callable_(**kwargs)

    def process(self, ...):
        ...
        kwargs = _prep_component_kwargs(...)
        res1 = self._invoke_component(app_state, component_callable, kwargs)
        # factory handling unchanged
```

Motivation: the only line tdom-svcs needs to substitute is
`component_callable(**kwargs)`. Without the hook, subclasses must clone ~17 lines
of surrounding bookkeeping (kwarg prep, factory pattern, error handling) to swap
that one line. With the hook, the ratio inverts: a 3-line override inheriting
all the rest. Future upstream improvements (factory handling, async, error
messages) flow through automatically.

The hook is purely additive: existing subclasses that override `process()`
directly still work. Single-method change, narrow signature, no protocol change.

Without `_invoke_component`, Stage 3 is still possible — tdom-svcs would keep
re-forking the body of `process()`. The fork would be smaller than today
(~30 lines instead of ~150) because Stage 2 removed the `str | Markup` and
`Markup` children handling, but it would still re-clone the factory dance and
type checks. Net cost: a few extra lines and continued maintenance burden any
time upstream's `process()` changes.

A symmetric `_resolve_callable(app_state, callable_)` hook is *not* requested.
Callable swap can use the existing transform-and-delegate pattern (override
`process()`, mutate `component_callable`, call `super().process()`). The
asymmetry is intentional: `_invoke_component` is the only line that *must* be
substituted from inside the body.

## Open questions / risks

1. **Upstream review/merge timing.** The `ian/integrations` branch is on a
   contributor remote, not yet merged to upstream main. We're not blocked: Stage
   3 applies the `_invoke_component` hook to a local workspace branch off
   `ian/integrations`, and the workspace pins to that. Upstream merge timing
   only affects how long we carry the local branch. If upstream merges with
   modifications to the hook signature, we rebase the workspace branch onto the
   merged version and adjust tdom-svcs's override accordingly (likely a 1-line
   change).
2. **Hopscotch impl override on Templates.** When `<{IHeader}>...</{IHeader}>`
   resolves `IHeader` to `Header`, the kwarg-prep step must use `Header`'s
   signature (defaults, extra fields). This is correct in both old and new
   upstream because the swap happens before kwarg prep. Verified in
   `tstring-html/tdom/processor_integration_test.py:117-147` (the `SystemComponentProcessor`
   pattern). Worth a regression test in tdom-svcs after Stage 3.
3. **`themester/views/__init__.py:get_view` change is non-trivial.** Currently
   inspects `__call__` signature for a `context` parameter to decide threading.
   Stage 2 step 2 collapses this. Worth a careful test pass on the view-resolution
   examples (`examples/views/*.py`).
4. **Tests that assert against `str(Markup(...))`.** Some themester tests may
   rely on the exact `Markup` wrapping behavior. Migration may flip these to
   plain `str` assertions. Should be obvious during test runs.
5. **Doctests / Sybil.** tdom-svcs uses Sybil to extract code blocks from docs.
   Migration of `docs/` markdown is required to keep these green.
6. **Direct `tdom.html` imports outside tdom-svcs/themester.** Stage 4 audit
   may surface consumers we don't know about (most likely in storyville's
   story renderer). Worst case, those need to migrate alongside; if migration
   is too disruptive, those consumers stay on direct `tdom.html` and the
   "everything via tdom-svcs" goal becomes "everything that needs DI".

## Sequencing

Recommended order:

1. **Now:** Stage 1 (cleanup against current upstream). Self-contained, low risk.
2. **In parallel with Stage 1:** open the upstream issue/PR for
   `_invoke_component`. Shorter argument since you can point to a Stage-1-cleaned
   tdom-svcs and say "the residual override is X lines, of which only 1 is the
   line we'd substitute."
3. **After Stage 1:** Stage 2 in sub-steps. Each commit is reviewable. The
   Protocol-update step gates the rest.
4. **After Stage 2:** Stage 3. Apply the `_invoke_component` hook to the
   workspace `tstring-html/` branch and port tdom-svcs onto it. ~half-day
   given the pre-work.
5. **After Stage 3:** Stage 4. Audit and switch direct `tdom.html` imports
   to `tdom_svcs.html` workspace-wide. ~half-day to 1 day depending on what
   the audit surfaces.

Total estimated effort: 4-6 days of focused work. Not blocked by upstream
review/merge — that runs concurrently as a separate track.
