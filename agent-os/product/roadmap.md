# Product Roadmap

1. [x] Minimal tdom Core Hooks — Add optional config/context parameters to tdom's component resolution, and implement
   pluggable hook system for component lifecycle (pre-resolution, post-resolution, rendering), keeping changes minimal
   and upstreamable. `S`

2. [ ] Basic svcs Container Integration — Create adapter layer that bridges tdom's component system with svcs container,
   implement DefaultInjector that resolves component dependencies from container, and add container initialization
   helpers. `S`

3. [ ] @Inject Decorator and Component Discovery — Implement @Inject decorator to mark injectable components, create
   package scanning utility to discover decorated components, and register them with the injector. `M`

4. [ ] Type-Safe Dependency Resolution — Add full type hint support for component dependencies, implement automatic
   resolution of Inject[T] type parameters using svcs-di, and validate dependencies at registration time with
   mypy/pyright integration. `M`

5. [ ] KeywordInjector with Props Override — Implement KeywordInjector that supports both injected services and explicit
   kwargs overrides, allowing template authors to override DI when needed while maintaining type safety. `S`

6. [ ] Resource-Based Component Resolution — Build HopscotchInjector foundation with resource-based component
   selection (tenant ID, feature flags, user role), enabling multiple implementations of same component interface to be
   resolved based on request context. `M`

7. [ ] Location-Based Component Selection — Extend HopscotchInjector with URL path-based component resolution, allowing
   different component implementations for different routes or site sections, with fallback chain for unmatched paths.
   `M`

8. [ ] Testing Utilities and Mock Injection — Create testing helpers for injecting mock services, implement test
   container fixtures, and provide examples of testing components in isolation with mocked dependencies. `S`

9. [ ] Component Lifecycle Middleware System — Implement pluggable middleware hooks for logging, validation,
   transformation, and error handling during component initialization and rendering phases. `M`

10. [ ] Performance Optimization and Caching — Add component resolution caching, optimize injector lookup performance,
    and implement lazy loading for component dependencies to minimize overhead. `M`

11. [ ] Documentation and Examples — Create comprehensive documentation covering basic DI patterns, advanced
    multi-implementation scenarios, testing strategies, and migration guides from manual service wiring to tdom-svcs.
    Include real-world examples for multi-tenancy and feature flags. `L`

12. [ ] Developer Experience Tools — Build CLI tools for component discovery validation, dependency graph visualization,
    and misconfiguration detection to help developers debug DI issues. `M`

> Notes
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature
> - Items 1-2 establish foundation (tdom hooks + svcs integration)
> - Items 3-5 build core DI functionality (discovery, resolution, overrides)
> - Items 6-7 add advanced resolution strategies (resources, locations)
> - Items 8-12 enhance DX (testing, middleware, performance, docs, tooling)
