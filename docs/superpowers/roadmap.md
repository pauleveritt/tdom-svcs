# Product Roadmap

## Phase 1: Foundation

1. [x] Minimal tdom Core Hooks — Add optional config/context parameters to tdom's component resolution, and implement
   pluggable hook system for component lifecycle (pre-resolution, post-resolution, rendering), keeping changes minimal
   and upstreamable. `S`

2. [x] Basic svcs Container Integration — Create adapter layer that bridges tdom's component system with svcs container,
   implement DefaultInjector that resolves component dependencies from container, and add container initialization
   helpers. `S`

## Phase 2: Core DI Functionality

3. [x] Component Discovery and Registration — Reuse svcs-di's @injectable decorator for marking components, create
   package scanning utility to discover decorated components, and register them in both ComponentNameRegistry (string
   names) and svcs container (type-based DI). `M`

4. [x] Component Lifecycle Middleware System — Implement pluggable middleware hooks for logging, validation,
   transformation, and error handling during component initialization and rendering phases using dict-like interfaces
   that work with or without svcs/svcs-di. `M`

5. [x] Documentation and Examples — Create comprehensive documentation covering basic DI patterns, advanced
   multi-implementation scenarios, testing strategies, and migration guides from manual service wiring to tdom-svcs.
   Include real-world examples for multi-tenancy and feature flags. `L`

## Phase 3: Middleware Examples & Services

6. [x] Aria Verifier Example — Add a middleware example before the path example. A simple component that returns a div
   with an `<img>` that has an `alt` attribute. Then another component that leaves out the alt. Wrap them both with
   middleware that logs warnings about missing alt attributes. Match all the patterns of other examples. `S`

7. [x] Path Middleware — Write a middleware example and docs that show path rewriting middleware. Use the specs
   in [tdom-path](/Users/pauleveritt/projects/t-strings/tdom-path/agent-os) for research. This effort will be different
   and simpler: you can register a service in the container that collects component paths and which assets are used and
   need copying. Keep this example simple. Explain the goal of using relative paths to actual things on disk during
   authoring, to let tooling help. To collect the path to the component, so you'll know where on disk it is relative
   too. An emphasis on standard Python path types. A way later to render relative to the path of a future request. `L`

8. [x] Reorganize Docs — Re-arrange README, delete the examples/node placeholder, and start a new page about the value
   of a standard Node type for Python web ecosystem interoperability. `S`

9. [x] Refactor Services to svcs-di Pattern — Break all services into svcs-di style modules. Each service should be its
   own Python module using the @injectable decorator for registration. Set up HopscotchRegistry and HopscotchContainer
   for scanning. Create `docs/services/` with narrative documentation for each service. Reference tdom-svcs examples
   for structure patterns. `M`

## Phase 4: Django Integration Research

10. [ ] Deep Research on Django Request Pipeline — Investigate Django's request processing to understand where to
    integrate HopscotchRegistry and HopscotchContainer. Currently middleware creates a container on each call, but we
    want one HopscotchContainer per Django request with easy access from views. Research where Django creates
    application-wide registries and integrate HopscotchRegistry as a quasi-global there. `L`

    Research areas:
    - Django's `AppConfig.ready()` for application-wide initialization
    - `django.core.handlers.base.BaseHandler` request processing
    - How `django.contrib.auth` and `django.contrib.messages` attach per-request state
    - Thread-local vs contextvars for request-scoped containers
    - ASGI vs WSGI differences for container lifecycle

11. [ ] Refactor tdom-django Middleware to @middleware Pattern — Rewrite the Django middleware as a dataclass using
    tdom-svcs's `@middleware` decorator. Use `__post_init__` to extract Django-specific data (request, response) into
    the standard middleware interface. Follow patterns from tdom-svcs middleware examples. `M`

12. [ ] Refactor For Inject Categories — In svcs-di there is an analysis file `FEATURE_CATEGORIES.md`. This project had
    a recent commit `Add registry introspection helpers`. See how the work in `svcs-di` injectable categories could
    change that commit and any other part of this project. `M`

13. [ ] Reduce Middleware to tdom-Specific Concerns — svcs-di now has its own middleware implementation. Refactor
    tdom-svcs to remove generic middleware functionality that's now in svcs-di, keeping only the tdom-specific
    integration code. Remove redundant code, tests, examples, and documentation. Update remaining docs to reference
    svcs-di middleware where appropriate. Focus on the unique value-add: how tdom components integrate with svcs-di
    middleware hooks during HTML rendering. `M`

## Phase 5: Performance & Developer Experience

14. [ ] Testing Utilities and Mock Injection — Create testing helpers for injecting mock services, implement test
    container fixtures, and provide examples of testing components in isolation with mocked dependencies. `S`

15. [ ] Performance Optimization and Caching — Add component resolution caching, optimize injector lookup performance,
    and implement lazy loading for component dependencies to minimize overhead. `M`

16. [ ] Developer Experience Tools — Build CLI tools for component discovery validation, dependency graph visualization,
    and misconfiguration detection to help developers debug DI issues. `M`

17. [x] Registry Introspection Helpers — Create `list_components()` and `list_middlewares()` helper functions for
    inspecting registered items. `list_components()` should return a dictionary mapping base component symbols to their
    variations (including target implementation, resource, and location for each `for_=` registration).
    `list_middlewares()` should return the registered middleware factories. These helpers enable runtime inspection
    and debugging of the registry state. `S`

## Phase 6: Dependency Modernization

18. [x] Add tdom-svcs to Workspace — Uncomment `tdom-svcs` from the root `pyproject.toml`
    workspace members list and resolve the resulting dependency graph. Verify that `uv sync`,
    `uv run pytest`, and `uvx ty check` all work from both the root workspace and the
    `tdom-svcs/` subdirectory. Update `tool.ty.environment.python` in `pyproject.toml` if the
    path changes. `S`

19. [x] Migrate Processor Off the Node-Based API — `processor.py` forks tdom's old internal
    node-object API (`tdom.nodes.Node/Element/Fragment/Text`, `_flatten_nodes`, `_node_from_value`,
    etc.) which no longer exists in tstring-html v0.1.15. Research the current `ProcessorService`
    class-based API and rewrite `processor.py` so `html()` returns `str`/`Markup` rather than
    a `Node` tree. Update the 49 `Node`/`Fragment`/`Element` type annotations and usages
    in tests and examples accordingly. `L`

20. [x] Drop `services/path/` — Asset management has been consolidated into `tdom-assets`
    (an svcs-native package). Remove the entire `src/tdom_svcs/services/path/` directory
    (`collector.py`, `middleware.py`, `types.py`, `__init__.py`), the `COMPONENT_LOCATION_PROP`
    constant from `tdom_svcs/types.py`, all tests in `tests/examples/middleware/test_path.py`,
    and the `examples/middleware/path/` example app. See `docs/research/drop-services-path.md`
    for the full migration mapping and verification checklist. `S`

21. [ ] Rename `tdom` Dependency to `tstring-html` — Update all `from tdom import` and
    `from tdom.X import` statements in `src/`, `tests/`, and `examples/` to use the new
    package import name (`tstring_html`). Update the `dependencies` list in `pyproject.toml`,
    the `tool.uv.sources` entry, and any documentation or docstring references to the old name.
    No behavior changes — mechanical rename only. `M`

## Phase 7: Port to Pluggable Component Processor

22. [x] Cleanup tdom-svcs Against Current Upstream — Drop the `dict | object | None`
    `ContextArg` type alias in favor of `svcs.Container | None`. Remove the
    `is_di_container` TypeGuard and `DIContainer` Protocol from `types.py`. Remove
    dict-handling branches in `processor.py`. Type `html()` signature as
    `html(template, *, container: svcs.Container | None = None) -> str | Markup`.
    Update tests in `test_html_wrapper.py` to remove dict-context parametrizations.
    No behavior changes for themester or tdom-assets — purely a type/dead-code
    cleanup that shrinks the fork before the larger port. See
    `docs/research/port-tstring-html-integrations.md` for the full plan. `S`

23. [x] Migrate Component Return Types to Template — Update component Protocols
    (`themester/views/decorators.py:View`, `themester/layouts/types.py:Layout`) to
    require `__call__(self) -> Template`. Migrate themester production code
    (`cli/layout_generate.py`, `layouts/decorators.py`, `views/decorators.py`,
    `views/__init__.py:get_view`), all examples, tests, and docs.
    Migrate tdom-svcs own examples and tests. Drop manual `context=` threading and
    `Markup(children)` wrapping; components return `t"..."` directly and let the
    processor recurse via `app_state`. tdom-svcs continues to support both
    `Template` and `str | Markup` returns during the migration window. See
    `tdom-svcs/docs/research/port-tstring-html-integrations.md` (Stage 2) for the
    full plan. `L`

24. [x] Port tdom-svcs to ian/integrations with `_invoke_component` Hook — Branch
    the workspace's `tstring-html/` off `ian/integrations` to a local branch (e.g.
    `pauleveritt/invoke-component-hook`), apply the `_invoke_component` hook
    (~6 lines) to `ComponentProcessor.process()`, and open the upstream PR
    concurrently. Replace tdom-svcs `processor.py` with a thin
    `DIComponentProcessor(ComponentProcessor[svcs.Container | None])` subclass
    (~30 lines) that overrides `process()` for impl-override and
    `_invoke_component` for DI injection. Delete the `_di_context` ContextVar
    transport, factory pattern handling, and children pre-rendering — all handled
    upstream now. See `tdom-svcs/docs/research/port-tstring-html-integrations.md`
    (Stage 3 and "Upstream ask" section) for the full plan. `M`

25. [x] Adopt tdom-svcs as Workspace-Wide Processor — Audit workspace for direct
    `from tdom import html` and `from tdom.processor import` usage. Switch each
    site to `from tdom_svcs import html`. Verify byte-identical output for the
    `container=None` path (e.g. compare a themester SSG build before/after).
    Decide whether to re-export `tdom.svg()` from tdom-svcs with a `container`
    parameter or leave direct imports. Optionally promote `tdom_svcs.html` as
    the workspace render entry point in workspace `README.md` and member
    `CLAUDE.md` files. See `tdom-svcs/docs/research/port-tstring-html-integrations.md`
    (Stage 4) for the full plan. `S`

## Phase 8: Resolution Strategy Refactor

After today's upstream activity in `tstring-html` `ian/integrations` (`a877d46`,
`9a5c37c`, `6fb4227`), the supported subclassing surface for DI changed from
"override `_invoke_component`" to "use `_prep_component_kwargs` flags + reordered
merge". The `_invoke_component` hook from item 24 was reverted. This phase
re-rewrites tdom-svcs's processor against the new surface (Option C: route
resolution through Hopscotch, delegate the call to `super().process()`), moves
the container from `app_state` to a ContextVar, and locks in `Get[T, Attr]` and
the rest of Hopscotch's resolution pipeline via regression tests.

26. [x] Track ian/integrations Directly — Replace the
    `pauleveritt/invoke-component-hook` workspace branch (which carried our reverted
    `_invoke_component` hook commit) with a direct checkout of `ian/integrations`.
    Branch deleted; workspace `tstring-html/` now follows `ian/integrations` HEAD
    (post-`6fb4227 Add exceptional flags`). No upstream patches required for the
    revised architecture. See
    `docs/research/port-tstring-html-integrations-revisited.md` ("Why this revision"
    and "Upstream changes — confirmed: none required" sections). `S`

27. [x] Rewrite tdom-svcs Processor per Option C — Replace the
    `_invoke_component`-based `DIComponentProcessor` with the four-phase Option C
    architecture in `src/tdom_svcs/processor.py`:

    1. Re-introduce `_di_context: ContextVar[svcs.Container | None]` (Stage 1's
       spec removed it; restore it).
    2. In `process()`: read container from cvar; swap component-level Protocol →
       impl via `_get_implementation`; if DI is needed, run the four phases:
       - **Phase 1** — pre-prep `partial_kwargs` with `_prep_component_kwargs(...,
         raise_on_missing=False)`.
       - **Phase 2** — resolve through Hopscotch via `build_resolved_kwargs(
         field_infos, HopscotchInjector(container)._resolve_field_value_sync,
         partial_kwargs)`.
       - **Phase 3** — compute `di_fill = (k, v) for k, v in resolved if k not in
         partial_kwargs`.
       - **Phase 4** — `super().process(..., provided_attrs=di_fill +
         provided_attrs)`. The factory branch in upstream captures
         component_object automatically.
    3. Delete the `_invoke_component` override (upstream method no longer exists
       post-`6fb4227`).
    4. Drop the `[svcs.Container | None]` parameterization on
       `DIComponentProcessor` and `TemplateProcessor`. Use upstream's
       `DefaultAppState = None`.
    5. Wrap `html()` body in `_di_context.set(container)` / `reset(token)`. Pass
       `app_state=None` to `_tp.process()`.
    6. Widen `needs_dependency_injection` to detect `info.operator is not None`
       (so components using only `Get[T, Attr]` still trigger DI).

    Imports four underscore-prefixed helpers (`_prep_component_kwargs`,
    `_resolve_t_attrs`, `get_callable_info` from `tdom.processor`;
    `_resolve_field_value_sync` method on `HopscotchInjector`) — all intentional
    surfaces post-`6fb4227`. Concentrate the imports in one method to limit drift
    blast-radius. See
    `docs/research/port-tstring-html-integrations-revisited.md` ("Revised
    architecture for tdom-svcs" and Q2 Option C sections). `M`

28. [x] Regression Tests for Full Hopscotch Resolution Surface — Add tests in
    `tdom-svcs/tests/` covering each Hopscotch feature now routed through Option
    C, with each test corresponding to a trace-through in the research doc:
    - `Inject[T]` basic resolution, with and without template override.
    - `Resource[T]` injection from `container.resource`.
    - `Get[T, Attr]` operator: DI-resolved (returns
      `container.get(T).attr`) AND template-overridden (template wins, no
      `container.get(T)` call — verify via a counter on a stub Settings service).
    - `Inject[svcs.Container]` self-injection: receives the container itself, not
      `container.get(svcs.Container)`.
    - Locator-aware `Inject[Protocol]`: register `IConfig` to `ConfigA` for
      `resource=Page`, `ConfigB` for `resource=Section`; render same component in
      both contexts; assert correct impl injected.
    - Component-level Protocol → impl override (`<{IHeader}>...</{IHeader}>` with
      `IHeader` registered to `Header`); kwarg prep uses `Header`'s field info.
    - Component_object capture under DI: factory class with `Inject[T]` fields;
      assert slot 2 of the returned tuple holds the constructed instance (test
      via a recording wrapper around `DIComponentProcessor`).
    - Required-DI-field fallback semantics: dataclass with required `Inject[T]`,
      no template attr; renders correctly without raising
      `TypeError: Missing required parameters`.
    - No-DI fast path: function component with no `Inject` / `Resource` / `Get`
      fields short-circuits to `super().process()` without resolution overhead.

    See `docs/research/port-tstring-html-integrations-revisited.md` (Stage 3
    "Add regression tests" subsection). `M`

29. [x] Type-Checking Improvements for the Rewrite — Parametrize
    `_get_implementation[T](container, cls: type[T]) -> type[T]` to carry the type
    through the Protocol → impl swap. Wrap `HopscotchInjector._resolve_field_value_sync`
    access in a single typed seam (one `# ty: ignore[private]` in a helper named
    `_make_resolver`). Add a Protocol-satisfaction test asserting
    `DIComponentProcessor` satisfies `IComponentProcessor[None]` per the workspace
    `protocol-satisfaction-test` standard. Verify `ty check` runs clean post-rewrite
    in `just quality`. See
    `docs/research/port-tstring-html-integrations-revisited.md` ("Type checking
    opportunities" section). `S`

30. [x] Cache Field-Info Helpers in svcs-hopscotch and svcs-di — Add
    `@functools.cache` to `hopscotch_get_field_infos` (`svcs-hopscotch/auto.py`) and
    `get_field_infos` (`svcs-di/auto.py`). Annotations are static per callable; the
    result is process-stable, identical across containers, and read-dominated. Apply
    the same `if "pytest" in sys.modules` toggle that `tdom`'s `get_callable_info`
    uses to avoid cross-test cache pollution. Independent perf win — speeds up both
    the current implementation and the post-port one (HopscotchInjector calls
    `get_field_infos_fn` on every `inject_target` invocation). Use `@functools.cache`
    rather than `@lru_cache(maxsize=N)` since callable count is bounded by code size.
    Same Python 3.14 thread-safety guarantee in both GIL and free-threaded builds.
    See `docs/research/port-tstring-html-integrations-revisited.md` ("Performance
    characteristics", "`functools.cache` vs `lru_cache(maxsize=N)`", and
    "Why `@lru_cache` and not svcs container caching?" sections). `S`

31. [x] Themester Worked Example for Get[T, Attr] — Once Phase 8's port lands,
    add a themester example demonstrating the `Get[T, Attr]` pattern as a
    replacement for dataclass `__post_init__`. Show side-by-side: a component with
    `Inject[Settings] + __post_init__` deriving `site_title` vs. the same component
    using `site_title: Get[Settings, "site_title"]` directly. Include docs
    explaining when each pattern is preferred. The user has flagged
    `Get[T, Attr]` as a load-bearing feature ("usually makes the postinit pattern
    unnecessary"); this example locks in the recommended pattern. See
    `docs/research/port-tstring-html-integrations-revisited.md` ("Open questions /
    risks" item 2 and Stage 3 verification step). `S`

32. [x] Eliminate `_tp` and `_default_ctx` Module Globals — Construct
    `TemplateProcessor` and `ProcessContext` per `html()` call rather than holding
    them at module level. Matches tdom's own test idioms (`_make_html()` closure
    capture in `processor_integration_test.py`, factory pattern in
    `processor_test.py`). Purely structural — no behavior change, no test changes
    expected. Verify byte-identical output for the existing test suite. This is
    the uncontroversial first step of the resolution-strategy alignment with svcs.
    See `docs/research/di-context-threading.md` ("Comparison: tdom's Own Patterns"
    and "Tradeoff Deep Dive"). `S`

33. [x] Move Container onto `DIComponentProcessor` (Option B) — Add
    `container: svcs.Container | None = None` as a frozen field on
    `DIComponentProcessor`. Replace every `_di_context.get()` read with
    `self.container`. Update `html()` to construct
    `DIComponentProcessor(container=container)` per call. Delete the
    `_di_context` ContextVar and its `set(...)/reset(token)` plumbing in `html()`.
    Update tests in `tests/test_processor_unit.py` and `tests/test_di_injection.py`
    that currently rely on the ContextVar transport (they should construct
    processors directly with the container, which simplifies the test setup).
    See `docs/research/di-context-threading.md` ("Decision: Option B + svcs as
    source of truth", step 1). `M`

34. [x] Register `TemplateProcessor` Per-Container via `svcs_container` — Define a
    `svcs_container(container)` setup function in tdom-svcs that the Hopscotch
    scanner discovers automatically. The function registers a `TemplateProcessor`
    (with `component_processor_api=DIComponentProcessor(container=container)`,
    plus `slash_void=True` and `uppercase_doctype=True`) as a local value on the
    container. Refactor `html()` to a thin dispatcher:

    - When `container is None`: delegate to plain `tdom.html(template)` — no DI
      pipeline needed.
    - When `container` is provided: resolve the registered `TemplateProcessor`
      via `container.get(TemplateProcessor)` and call
      `tp.process(template, ProcessContext(), app_state=None)`.

    End-state: zero module-level mutable state in `processor.py`. svcs is the
    single source of truth for the rendering pipeline. Allocation cost is
    mitigated — `TemplateProcessor` is constructed once per container and reused
    across all `html()` calls on that container. Verify the scanner picks up the
    setup function automatically (no explicit registration required at app
    startup). See `docs/research/di-context-threading.md` ("Decision: Option B +
    svcs as source of truth", steps 2 and 3). `M`

35. [ ] Workspace Member Audit and Verification — Items 32–34 preserve the public
    `html(template, *, container=None) -> str | Markup` signature, but eliminate
    module-level `_di_context`, `_tp`, and `_default_ctx`. Verify downstream
    consumers still work:

    - **themester**: 3 example apps import `html` (`examples/get_operator/`,
      `examples/layouts/multi_layer/`, plus production `views/`/`layouts/`).
      Run `just test` and confirm any rendered output is byte-identical.
    - **tdom-layout**: production code in `src/tdom_layout/config_based.py`
      and tests in `tests/test_placeholder_processor.py`,
      `tests/test_integration.py`. Run `just test`.
    - **storyville**: 30+ example components and stories that import
      `html` from `tdom_svcs`. Run example smoke tests; visual outputs unchanged.
    - **tdom-svcs itself**: `tests/test_processor_unit.py`,
      `tests/test_hopscotch_resolution.py`, `tests/test_di_injection.py`, plus
      all examples in `examples/`.

    Workspace-wide grep for `_di_context` after the refactor — no remaining
    references should exist outside tdom-svcs's git history. Same for any docs
    or comments in other packages that describe the ContextVar transport. The
    workspace `README.md` reference to `from tdom_svcs import html` continues to
    be the canonical pattern. `S`

36. [ ] Documentation Refresh for the svcs-as-Source-of-Truth Architecture —
    Update tdom-svcs documentation to reflect items 32–34:

    - **`docs/core_concepts.md`**: Add a section explaining the `svcs_container`
      setup function pattern; note that `TemplateProcessor` lifecycle is managed
      by svcs and is overridable via container registration.
    - **`docs/getting_started.md`**: Verify the basic `html()` usage example
      still works without modification (it should — public API unchanged). Add
      a short note about how DI is wired internally for readers curious about
      the mechanism.
    - **`docs/research/di-context-threading.md`**: Already updated with the
      decision; mark Phase 8 items 32–34 as the implementation.
    - **`CLAUDE.md`** (project- and workspace-level): If guidance describes the
      ContextVar transport, update to describe the registry-based approach.
    - **`processor.py` module docstring**: Replace the current "ContextVar leaves
      app_state free for user-defined state" rationale with a note describing
      the `svcs_container` setup function and the registry-as-source-of-truth
      design.

    Add an example file (`examples/basic/svcs_container_setup/`) showing how an
    application with a custom `TemplateProcessor` configuration would override
    the default via its own `svcs_container` setup function. `S`

## Phase 9: Rebaseline Against Merged tdom Main

PR #118 (`Component Process API Remix`) merged Ian's processor work into
`t-strings/tdom` `main` as squash commit `b2287f1` on 2026-05-03. The local
workspace checkout is still on `ian/integrations` at `6fb4227`, which is
patch-equivalent to PR commit `c1e9370`, but the merged PR head (`80a7ade`) made
one more important simplification pass: `app_state`, `DefaultAppState`, generic
`IComponentProcessor[T]`, and component-object capture were removed from the
public processor extension shape. The remaining intentional integration surface is
`ComponentProcessor.process()`, `_prep_component_kwargs()` with the
`raise_on_missing` / `raise_on_requires_positional` flags, `_resolve_t_attrs()`,
and optional `assume_ctx` on `html()` / `svg()`.

37. [x] Rebaseline tdom-svcs Processor for PR #118 — Move the workspace
    `tstring-html/` member from local `ian/integrations` to merged `tdom` `main`
    (`b2287f1` / `v0.1.15`) and update `tdom-svcs` to the final non-generic
    processor API:

    - Update `src/tdom_svcs/processor.py` imports and signatures:
      remove `DefaultAppState` and `ComponentObject`; make
      `DIComponentProcessor.process()` accept
      `(template, last_ctx, component_callable, attrs, component_template,
      provided_attrs=())` and return `Template`; update all `super().process()`
      calls; call `tp.process(template, ProcessContext())` without `app_state`.
    - Preserve the current four-phase Option C resolution strategy:
      pre-prep partial kwargs with `_prep_component_kwargs(...,
      raise_on_missing=False, raise_on_requires_positional=False)`, resolve
      through `build_resolved_kwargs()` and Hopscotch, compute `di_fill`, then
      delegate invocation to `super().process(..., provided_attrs=di_fill +
      provided_attrs)`.
    - Remove component-object capture as a tdom-svcs contract. Delete or rewrite
      `tests/test_hopscotch_resolution.py::test_component_object_capture_factory`
      and any comments/docs that claim `super().process()` returns
      `(Template, ComponentObject | None)`. Keep factory-component rendering
      coverage, but assert rendered behavior rather than instance capture.
    - Update type checks and protocol assertions:
      `IComponentProcessor` is no longer subscriptable, so replace
      `IComponentProcessor[None]` assertions with the new non-generic protocol
      shape.
    - Refresh research and roadmap references that became stale after PR #118:
      `docs/research/port-tstring-html-integrations-revisited.md`,
      `docs/research/di-context-threading.md`, and Phase 8 wording that treats
      `DefaultAppState`, `app_state`, or component-object capture as
      load-bearing. Keep the historical context, but add a clear "superseded by
      PR #118" note where appropriate.
    - Re-evaluate the optional upstream asks in the backlog. Publicizing
      `_prep_component_kwargs` / `_resolve_t_attrs` remains useful because
      tdom-svcs now depends on them directly; a `ComponentProcessor`
      `prep_partial_kwargs()` helper is still nice-to-have, but no longer needs
      to account for component-object capture.

    Verification: run `just quality && just test` in `tdom-svcs`; run the
    affected downstream smoke checks in `themester`; and confirm there are no
    remaining imports or references to `DefaultAppState`, `IComponentProcessor[...]`,
    `app_state=` on `TemplateProcessor.process()`, or component-object capture in
    executable code. `M`

    Completed 2026-05-04: `tdom-svcs` now targets merged `tdom` main at
    `b2287f1`; `just quality`, `just test`, and Sphinx `-W` pass in
    `tdom-svcs`; `just quality` and `just test` pass in `themester`; executable
    stale-API searches are clean.

## Phase 10: Component Decision Evidence

After Phase 9 rebaselines the processor against merged `tstring-html`, tdom-svcs
should expose component-rendering decisions in the same style as Hopscotch
resolution evidence. This is a consumer of `svcs-di`/`svcs-hopscotch` decision
algebra, not a separate router.

38. [x] P1 Lean Component Resolution Inspection — Add a small internal inspection
    helper for the component resolution choice only: native tag vs component,
    Protocol → implementation swap, and final callable target. Do not include
    per-field DI fills, children provenance, or Hopscotch resolver evidence in
    this first item. Acceptance: unit tests can inspect the helper for a plain
    component and a Protocol component overridden through Hopscotch; rendered
    output is unchanged. `S`

    Completed 2026-05-05: `ComponentResolutionDecision` and
    `_inspect_component_resolution()` now describe native tags, plain
    components, and Hopscotch implementation swaps without collecting DI fill
    evidence. `DIComponentProcessor.process()` uses the same decision object for
    its final callable choice. `tests/test_processor_unit.py` covers native
    tags, plain components, class overrides, Protocol overrides, and verifies
    Protocol override rendering still produces the same output.

39. [x] P1 DI Fill Evidence Propagation — After Hopscotch has adopted the
    svcs-di resolver algebra and lean locator inspection, preserve limited
    per-field source evidence during component rendering: template attr,
    injected dependency, `Get[T, Attr]`, `Resource[T]`, or default. Acceptance:
    `Get[T, Attr]` and resource-driven component examples expose evidence without
    changing rendered output. `M`

    Completed 2026-05-05: Hopscotch roadmap items 34 and 35 are done, so this
    package now resolves component fields through `_resolve_component_field_fills()`.
    The helper returns resolved kwargs plus `ComponentFieldEvidence` records with
    lean source labels for template attrs, injected dependencies, field
    operators, resources, and defaults. `DIComponentProcessor.process()` uses the
    same helper for rendering, preserving output behavior. Regression tests cover
    `Get[T, Attr]`, `Resource[T]`, template override, injected dependency, and
    default evidence.

    2026-05-05 router-spike scheduling note: tdom-svcs already exposes the
    component-resolution and field-fill evidence needed for Tainie's next
    decision-evidence slice. Do not make TypeForm, Sentinel, or Storyville witness
    work a prerequisite for the overnight router spike. The next cross-package
    pressure should come from Tainie consuming a small selected/no-match artifact
    and reporting whether component evidence needs another field.

    2026-05-06 judge-confidence scheduling note: keep the next overnight loop
    focused on existing tdom-svcs component-resolution and field-fill evidence
    paired with Hopscotch route artifacts. The useful work is a compact consumer
    packet or fixture evidence shape for Tainie, plus negative/no-container or
    required-DI cases. Do not start Storyville witness enrichment or unsupported
    TypeForm/Sentinel API work before Tainie proves a concrete consumer need.

40. [ ] P2 TypeForm and Sentinel Deferral — Keep component typing on the supported
    `ty` surface (`TypeIs`, `Literal`, `TypedDict`, `ReadOnly`, `ParamSpec`) and
    avoid public `TypeForm` or typed `Sentinel` APIs until Tainie's conformance
    watch says they pass. Acceptance: docs name the gate and link to the current
    probe results. `S`

## Phase 11: Package-Local Domain Source

This phase makes `tdom-svcs` the next consumer of the `tainie-tools` domain
authoring work after `svcs-hopscotch`. The goal is not to invent a
tdom-svcs-specific domain system. The goal is to prove that the shared
DomainPack authoring policy, directive vocabulary, validation expectations, and
future inventory export are reusable across a second package with different
native concepts.

tdom-svcs is a good second consumer because its package-local domain sits at a
different boundary from Hopscotch: t-string component rendering, optional DI
context, component implementation overrides, injected props, field operators,
and the plain no-container rendering path. Those concepts should stress the
policy without needing Storyville-specific witness metadata yet.

41. [x] P0 Align With `tainie-tools` Domain Authoring Policy — Wait for the
    `tainie-tools` Domain Authoring Policy spec to define the advisory rules for
    `planned` vs. `verified`, concept/rule/witness usage, prose-vs-directive
    boundaries, drift-resistance expectations, and when docs should defer to
    derived facts. Acceptance: this roadmap item points at the accepted
    `tainie-tools` policy spec, and no tdom-svcs-specific convention contradicts
    it. `S`

    Completed 2026-05-05: `tainie-tools` published
    `docs/domain-authoring-policy.md` and marked Domain Authoring Policy done in
    its roadmap. tdom-svcs now follows that policy in `docs/domain/index.md`
    rather than inventing a package-local convention.

42. [x] P0 Draft tdom-svcs Package-Local Domain Source — Add
    `docs/domain/index.md` as a friendly package-local domain source and link it
    from `docs/index.md`. Start advisory-first: prose for intent and small
    `domain:concept`, `domain:rule`, and `domain:witness` directives for
    checkable facts. Candidate concepts: `html()` render entry point,
    `DIComponentProcessor`, container context, component implementation
    override, injected component field, `Resource[T]`, `Get[T, Attr]`, template
    kwargs override, and no-container rendering. Acceptance: docs build with
    `tainie_tools.sphinx` enabled, the page remains readable as documentation,
    and verified facts use symbol paths or package path strings where possible.
    `M`

    Completed 2026-05-05: added `docs/domain/index.md`, linked it from
    `docs/index.md`, enabled `tainie_tools.sphinx`, and verified the docs build.
    The first facts cover `html()`, `DIComponentProcessor`, `Inject[T]`,
    `Resource[T]`, `Get[T, Attr]`, no-container rendering, template override
    precedence, Hopscotch-backed component DI, downstream-owned resource shape,
    and the testing boundary between string assertions and HTML-aware
    structural assertions.

43. [x] P0 Promote Existing Examples And Tests As Witnesses — Use existing
    examples and regression tests as the first tdom-svcs witnesses instead of
    inventing sidecar metadata. Start with examples and tests that already cover
    no-container rendering, `Inject[T]`, `Resource[T]`, `Get[T, Attr]`,
    template-override precedence, locator-aware component overrides, and
    required DI fallback behavior. Acceptance: each verified rule has at least
    one checkable witness target, witness links reference known concepts or
    rules, and Storyville-specific witness semantics remain deferred. `M`

    Completed 2026-05-05: `docs/domain/index.md` now uses existing regression
    tests and the pure tdom example as verified witnesses. Witnesses cover
    no-container rendering, `Inject[T]`, `Resource[T]`, `Get[T, Attr]`,
    template override precedence, component implementation override, and
    required DI fallback behavior. Storyville-specific witness metadata remains
    deferred.

44. [x] P1 Add Package-Local Domain Validation To CI — After `tainie-tools`
    provides the shared package-local validation path, configure tdom-svcs
    through project configuration rather than custom glue code. Keep only a
    small package-local test that invokes the shared validator against
    `docs/domain/`. Acceptance: CI validates syntax, target resolution,
    duplicate ids, and verified-link structure without copying validation logic
    from `tainie-tools` or `svcs-hopscotch`. `S`

    Completed 2026-05-05: `docs/conf.py` enables
    `tainie_domain_inventory_path`, and `tests/test_domain_inventory.py` runs a
    warning-as-error docs build. Validation issues are emitted by the shared
    `tainie_tools.sphinx` extension and asserted empty from the generated
    inventory.

45. [x] P1 Exercise Domain Inventory Export — After `tainie-tools` adds stable
    JSON inventory export, make tdom-svcs the second integration target after
    svcs-hopscotch. Acceptance: the exported inventory includes tdom-svcs
    concepts, rules, witnesses, source provenance, statuses, and resolved target
    metadata, and the export does not require running Tainie. `M`

    Completed 2026-05-05: the docs build now writes
    `domain-inventory.json`, and `tests/test_domain_inventory.py` asserts the
    schema version, empty validation issues, `domain/index` source provenance,
    verified concept status, resolved symbol metadata, resolved witness target
    metadata, and the resource witness link to
    `resource-shape-is-downstream-owned`.

46. [x] P2 Revisit Storyville Witnesses Later — Once Storyville's package-local
    story metadata shape is settled, decide whether tdom-svcs component stories
    should become richer witnesses than plain examples/tests. Acceptance: any
    Storyville integration builds on the generic witness model rather than
    changing the tdom-svcs domain source format retroactively. `S`

    Completed 2026-05-06: Storyville settled a first typed domain evidence
    shape with optional `DomainStory` and `DomainSubject` packets plus
    `collect_domain_evidence()`. tdom-svcs now includes
    `examples/domain_stories/` and `tests/examples/test_domain_stories.py`,
    which prove two component stories can act as richer witnesses while the
    authoritative domain rule source remains `docs/domain/index.md`.

47. [x] P1 Tainie Component Evidence Provider Integration — Tainie's P3a-P5
    evidence-provider gates have landed, including the native provider registry,
    Pydantic Evals parity, svcs-hopscotch producer registration, and live
    evidence classification. Promote the judge-confidence component packet from
    an inspection helper into a package-owned producer that Tainie can call
    through its provider contract. Acceptance: public Tainie native and
    Pydantic eval entrypoints can attach trusted `tdom-svcs` component evidence
    for selected overrides, no-container components, required-DI blockers, and
    field-source labels; malformed provider output is quarantined as provider
    drift; rendered output is unchanged; no Tainie module import requires
    importing `tdom_svcs` unless the caller opts into the provider. `M`

    Completed 2026-05-06: `tdom-svcs` now projects component inspection packets
    into Tainie's trusted component evidence report shape, and Tainie can attach
    that evidence through an opt-in `component_provider` lane across native and
    Pydantic Evals entrypoints. Provider drift is quarantined, missing producers
    yield zero evidence, and Tainie imports stay free of `tdom_svcs` unless the
    caller opts into the component producer registration helper.

## Phase 12: Documentation Restructure

Align tdom-svcs docs to the shared workspace outline while preserving the
existing strong guide, examples, services, and domain material.

- Add or sharpen "Why tdom-svcs?" around plain `html()` first and optional
  container-aware rendering second.
- Keep Getting Started, core concepts, Node, and How It Works in Concepts and
  Guides.
- Keep services and API under Reference.
- Keep Domain as a first-class section.
- Keep research and excluded Superpowers history under Development unless
  intentionally published.

48. [ ] README Overhaul — Rewrite `README.md` against the shared README policy.
    Keep the plain `html()` first, optional container-aware rendering second
    positioning; shorten extended examples; verify docs links, badges, project
    URLs, and current imports; and move deeper DI/Hopscotch walkthroughs into
    Sphinx docs. Acceptance: README follows
    `docs/superpowers/policies/readme.md`, install uses `uv` first, Quick Start
    is compact and current, and GitHub/PyPI metadata is consistent. `M`

49. [x] P1 Complete Example Bundle Migration — `docs/examples/hopscotch/resource.md`
    is the multi-file pilot, and `tainie-tools` Example Bundle Authoring is now
    done. Migrate the remaining `docs/examples/**` pages from brittle
    `literalinclude` anchors to named `example-snippet`/`example-source`
    directives, adding manifests where examples are multi-file bundles and
    domain metadata where the example names known concepts or rules. This feeds
    Tainie's future Example Inventory Evidence Input work without making Tainie
    import producer docs. Acceptance: `uv run pytest tests/test_examples.py -q`,
    Sphinx `-W`, generated `example-inventory.json` has no validation issues,
    and migrated pages no longer use `:start-at:` / `:end-at:` anchors. `M`

    Completed 2026-05-06: Basic, Categories, Hopscotch, and Middleware example
    docs now use `example-snippet` and `example-source` instead of brittle
    `literalinclude`, `:start-at:`, or `:end-at:` anchors. Multi-file examples
    have package-local `example.toml` manifests, Sphinx emits
    `example-inventory.json`, and the migration is guarded by
    `tests/test_example_docs_migration.py`.

50. [ ] P2 Apply Shared Docs Outline — Restructure the published docs navigation
    after the example migration, so examples and inventories remain stable while
    pages move. Acceptance: docs expose a concise "Why tdom-svcs?" entry point,
    Concepts/Guides/Reference/Domain/Development sections match the shared
    workspace outline, redirects or links preserve existing high-value pages,
    and Sphinx `-W` plus domain/example inventory tests pass. `M`

51. [ ] P2 Shared Example Policy Alignment Audit — After Themester finishes the
    example prep-inventory policy, audit the completed tdom-svcs example bundle
    migration against the shared workspace conventions. Confirm whether
    tdom-svcs has a suitable getting-started example set, whether canonical
    bundles use stable concept-oriented IDs, and whether multi-file examples use
    `app.py` with `main()` plus `example.toml` where practical. Do not churn
    already-migrated examples unless the policy reveals a user-facing mismatch.
    Acceptance: audit records either no-op rationale or a focused follow-up list;
    existing `example-inventory.json`, Sphinx `-W`, and example tests remain
    green. `S`

## Phase 13: Tainie DomainSpec Producer Pilot

Tainie owns the canonical DomainSpec/DomainPack compiler and consumer model.
tdom-svcs should not invent that shape locally. Its role is to be a real
producer fixture with validated package-local domain, example, Storyville, and
component-evidence artifacts that Tainie can consume through public provider or
inventory contracts.

51. [ ] P1 DomainSpec Inventory Pilot For Tainie — Tainie A-18 is the immediate
    DomainPack compiler scoping pass; this producer-side inventory pilot is not
    a blocker for that design doc, but is the natural prerequisite for the first
    compiler implementation because tdom-svcs has both `domain-inventory.json`
    and `example-inventory.json` plus the three hand-written pack families that
    proved lift (`props-priority`, `canonical-component-shape`, and
    `service-injection-shape`). Acceptance: Tainie can read tdom-svcs inventories
    as trusted passive evidence without importing Sphinx or producer docs;
    metrics distinguish domain inventory evidence, example inventory evidence,
    Storyville witness evidence, component provider evidence, compiled pack
    evidence, and model-authored claims; tdom-svcs keeps docs/domain as the
    authored source of truth; the producer inventory contains enough source and
    witness metadata for Tainie's compiler scoping to detect stale pack fields or
    missing witnesses before generating a pack. `M`

## Backlog

- [ ] Hygiene fixes from 2026-05-08 deep-dive audit — Three small unrelated
  items flagged by the cross-workspace audit (subagent surveyed tdom-svcs
  boundary): (a) `tests/test_html_wrapper.py:9` does `import tdom` directly,
  violating the workspace `from tdom_svcs import html` rule (the file also
  imports `tdom_svcs.html` separately at `:13`; the bare `tdom` import is for
  Node comparison in test internals — fix or document why the rule does not
  apply here). (b) Public introspection/scanning/middleware surfaces use
  `registry: Any` extensively (`introspection.py:60,111`,
  `scanning.py:20,23`, `middleware.py:46,57,82,103,117,134`); not a bug, but
  a typing-debt review candidate. (c) No Tainie test exercises
  `inspect_component_evidence_packet()` against a live svcs container — the
  Tainie round-trip tests construct packets manually
  (`tainie/tests/test_evidence_providers.py:626-680`); add one that drives
  the full producer path so the contract is end-to-end pinned. Acceptance:
  test-html-wrapper-rule fix or documented exception; typing-debt note
  filed; one Tainie test runs `inspect_component_evidence_packet()`
  end-to-end. `S`

- [x] Fix stale `register_component` docs — several docs pages still use the old name
  (`register_component`) that was renamed to `register_hookable` in a prior refactor. Files
  affected: `docs/api_reference.md` (function signature and examples), `docs/examples/categories/
  imperative_categories.md` (description, code examples, and a broken `literalinclude` path
  pointing to the non-existent `imperative_categories.py` instead of `categories_example.py`),
  `docs/examples/index.md` (table row with broken file link and stale description),
  `docs/examples/categories/index.md` (code example). Mechanical rename only — no behavior
  changes. `S`

- [x] Retire stale storyville pytest plugin breakage note — `storyville` registered a
  `pytest11` entrypoint that previously imported `from tdom import Node`, causing
  `tdom-svcs` pytest startup to fail unless the plugin was disabled. Verified
  2026-05-05: `tdom-svcs` no longer needs a local `-p no:storyville` workaround;
  `just test` starts pytest with the workspace plugins available and passes.
  Storyville's own package migration remains tracked in the Storyville roadmap,
  not here. `S`

- [ ] Optional upstream ask: drop the `_` prefix on `_prep_component_kwargs` and
  `_resolve_t_attrs` in `tstring-html/tdom/processor.py`. Since `6fb4227`'s flags
  (`raise_on_missing`, `raise_on_requires_positional`) were added explicitly to
  support DI subclasses calling `_prep_component_kwargs` directly, the function is
  now part of the intentional public surface. The `_` prefix is misleading. Same
  reasoning for `_resolve_t_attrs`. Mechanical rename only. tdom-svcs would update
  the corresponding imports in Phase 8 item 27. See
  `docs/research/port-tstring-html-integrations-revisited.md` ("Imports of
  underscore-prefixed helpers" subsection). `S`

- [ ] Optional upstream ask: bundle Phase 1 into a `ComponentProcessor` static
  helper in `tstring-html/tdom/processor.py`. Adding a `@staticmethod
  prep_partial_kwargs(component_callable, template, attrs, component_template,
  provided_attrs)` to `ComponentProcessor` would let DI subclasses call one method
  instead of importing three private helpers (`_prep_component_kwargs`,
  `_resolve_t_attrs`, `get_callable_info`) and threading them together. Saves
  subclasses ~6 lines and reduces the surface tdom-svcs imports. tdom-svcs ships
  fine without it. See
  `docs/research/port-tstring-html-integrations-revisited.md` ("Upstream changes —
  confirmed: none required" section, second nice-to-have). `S`

> Notes
> - Maintain roadmap entries using
>   [Roadmap Standards](roadmap-standards.md): priority, context, acceptance,
>   size, explicit dependencies, and clear deferrals.
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature
> - Phase 1: Foundation (tdom hooks + svcs integration)
> - Phase 2: Core DI functionality (discovery, resolution, middleware)
> - Phase 3: Middleware examples and services refactoring
> - Phase 4: Django integration research and patterns
> - Phase 5: Performance and developer experience enhancements
> - Phase 6: Dependency modernization (workspace, rename, API migration)
> - Phase 7: Port to pluggable component processor (cleanup, Template migration, ian/integrations port, workspace adoption)
> - Phase 8: Resolution strategy refactor (Hopscotch resolution through `super()` per upstream's `6fb4227` flags-based subclassing surface; subsequently, eliminate module-level globals in `processor.py` and make svcs the source of truth for the rendering pipeline via per-container `TemplateProcessor` registration — see `docs/research/di-context-threading.md`)
> - Phase 9: Rebaseline against merged `tdom` main after PR #118 (`b2287f1`), adapting tdom-svcs from the local `ian/integrations` API to the final non-generic processor extension shape with no `app_state`, no `DefaultAppState`, and no component-object capture
> - Phase 11: Package-local DomainPack source, using tdom-svcs as the second `tainie-tools` domain authoring consumer after svcs-hopscotch
> - Phase 12: Public docs and example inventory cleanup, sequenced before Tainie consumes package example inventories
> - Phase 13: tdom-svcs as a DomainSpec/DomainPack producer pilot; Tainie owns the canonical consumer/compiler contract
