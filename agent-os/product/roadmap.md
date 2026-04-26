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
