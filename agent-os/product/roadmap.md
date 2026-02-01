# Product Roadmap

1. [x] Minimal tdom Core Hooks — Add optional config/context parameters to tdom's component resolution, and implement
   pluggable hook system for component lifecycle (pre-resolution, post-resolution, rendering), keeping changes minimal
   and upstreamable. `S`

2. [x] Basic svcs Container Integration — Create adapter layer that bridges tdom's component system with svcs container,
   implement DefaultInjector that resolves component dependencies from container, and add container initialization
   helpers. `S`

3. [x] Component Discovery and Registration — Reuse svcs-di's @injectable decorator for marking components, create
   package scanning utility to discover decorated components, and register them in both ComponentNameRegistry (string
   names) and svcs container (type-based DI). `M`

4. [x] Component Lifecycle Middleware System — Implement pluggable middleware hooks for logging, validation,
   transformation, and error handling during component initialization and rendering phases using dict-like interfaces
   that work with or without svcs/svcs-di. `M`

5. [x] Documentation and Examples — Create comprehensive documentation covering basic DI patterns, advanced
   multi-implementation scenarios, testing strategies, and migration guides from manual service wiring to tdom-svcs.
   Include real-world examples for multi-tenancy and feature flags. `L`

6. [x] Aria Verifier Example — Add a middleware example before the path example. A simple component that returns a div
   with an `<img>` that has an `alt` attribute. Then another component that leaves out the alt. Wrap them both with
   middleware that logs warnings about missing alt attributes. Match all the patterns of other examples. `S`

7. [x] Path Middleware — Write a middleware example and docs that show path rewriting middleware. Use the specs
   in [tdom-path](/Users/pauleveritt/projects/t-strings/tdom-path/agent-os) for research. This effort will be different
   and simpler: you can register a service in the container that collects component paths and which assets are used and
   need copying. Keep this example simple. Explain the goal of using relative paths to actual things on disk during
   authoring, to let tooling help. To collect the path to the component, so you'll know where on disk it is relative
   too. An emphasis on standard Python path types. A way later to render relative to the path of a future request. `L`

8. [ ] Testing Utilities and Mock Injection — Create testing helpers for injecting mock services, implement test
   container fixtures, and provide examples of testing components in isolation with mocked dependencies. `S`

9. [ ] Performance Optimization and Caching — Add component resolution caching, optimize injector lookup performance,
   and implement lazy loading for component dependencies to minimize overhead. `M`

10. [ ] Developer Experience Tools — Build CLI tools for component discovery validation, dependency graph visualization,
    and misconfiguration detection to help developers debug DI issues. `M`

> Notes
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature
> - Items 1-2 establish foundation (tdom hooks + svcs integration)
> - Items 3-5 build core DI functionality (discovery, resolution, overrides)
> - Items 6-7 add advanced resolution strategies (resources, locations)
> - Items 8-12 enhance DX (testing, middleware, performance, docs, tooling)
