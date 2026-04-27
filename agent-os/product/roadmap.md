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
    `views/__init__.py:get_view`), all examples, tests, docs, and lat.md sections.
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

28. [x] Rewrite tdom-svcs Processor per Option C — Replace the
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

29. [x] Regression Tests for Full Hopscotch Resolution Surface — Add tests in
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

30. [x] Type-Checking Improvements for the Rewrite — Parametrize
    `_get_implementation[T](container, cls: type[T]) -> type[T]` to carry the type
    through the Protocol → impl swap. Wrap `HopscotchInjector._resolve_field_value_sync`
    access in a single typed seam (one `# ty: ignore[private]` in a helper named
    `_make_resolver`). Add a Protocol-satisfaction test asserting
    `DIComponentProcessor` satisfies `IComponentProcessor[None]` per the workspace
    `protocol-satisfaction-test` standard. Verify `ty check` runs clean post-rewrite
    in `just quality`. See
    `docs/research/port-tstring-html-integrations-revisited.md` ("Type checking
    opportunities" section). `S`

27. [x] Cache Field-Info Helpers in svcs-hopscotch and svcs-di — Add
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
    using `site_title: Get[Settings, "site_title"]` directly. Include lat.md
    sections explaining when each pattern is preferred. The user has flagged
    `Get[T, Attr]` as a load-bearing feature ("usually makes the postinit pattern
    unnecessary"); this example locks in the recommended pattern. See
    `docs/research/port-tstring-html-integrations-revisited.md` ("Open questions /
    risks" item 2 and Stage 3 verification step). `S`

## Backlog

- [ ] Fix stale `register_component` docs — several docs pages still use the old name
  (`register_component`) that was renamed to `register_hookable` in a prior refactor. Files
  affected: `docs/api_reference.md` (function signature and examples), `docs/examples/categories/
  imperative_categories.md` (description, code examples, and a broken `literalinclude` path
  pointing to the non-existent `imperative_categories.py` instead of `categories_example.py`),
  `docs/examples/index.md` (table row with broken file link and stale description),
  `docs/examples/categories/index.md` (code example). Mechanical rename only — no behavior
  changes. `S`

- [ ] Fix storyville pytest plugin breakage — `storyville` registers a `pytest11` entrypoint
  in the workspace venv that imports `from tdom import Node`. Since `Node` was removed from
  tdom (now `tstring-html`), pytest fails to start without `-p no:storyville`. Fix by updating
  storyville to drop the `Node` import, or configure `pytest.ini`/`pyproject.toml` in tdom-svcs
  to suppress the broken plugin via `addopts = -p no:storyville`. `S`

- [ ] Optional upstream ask: drop the `_` prefix on `_prep_component_kwargs` and
  `_resolve_t_attrs` in `tstring-html/tdom/processor.py`. Since `6fb4227`'s flags
  (`raise_on_missing`, `raise_on_requires_positional`) were added explicitly to
  support DI subclasses calling `_prep_component_kwargs` directly, the function is
  now part of the intentional public surface. The `_` prefix is misleading. Same
  reasoning for `_resolve_t_attrs`. Mechanical rename only. tdom-svcs would update
  the corresponding imports in Phase 8 item 28. See
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
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature
> - Phase 1: Foundation (tdom hooks + svcs integration)
> - Phase 2: Core DI functionality (discovery, resolution, middleware)
> - Phase 3: Middleware examples and services refactoring
> - Phase 4: Django integration research and patterns
> - Phase 5: Performance and developer experience enhancements
> - Phase 6: Dependency modernization (workspace, rename, API migration)
> - Phase 7: Port to pluggable component processor (cleanup, Template migration, ian/integrations port, workspace adoption)
> - Phase 8: Resolution strategy refactor (ContextVar container transport + Hopscotch resolution through `super()`, responding to upstream's `6fb4227` flags-based subclassing surface)
