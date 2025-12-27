# Product Mission

## Pitch
tdom-svcs is an integration library that helps Python web developers build component-based UI systems with dependency injection by providing seamless integration between tdom (Template DOM for Python 3.14 t-strings) and svcs (service container), enabling automatic service injection into template components while keeping the core tdom library minimal and dependency-free.

## Users

### Primary Customers
- **Python Web Developers**: Teams building web applications with Python 3.14+ who want modern templating with dependency injection
- **Component Library Authors**: Developers creating reusable component systems that need service dependencies
- **Enterprise Development Teams**: Organizations building multi-tenant or location-aware applications with context-specific component behavior

### User Personas

**Frontend-Focused Python Developer** (25-40 years)
- **Role:** Full-stack Python developer building web UIs
- **Context:** Building modern web applications with Python 3.14+ t-strings, wants React-like component patterns with DI
- **Pain Points:** Tired of passing services through multiple component layers; wants clean separation between presentation and business logic; needs type-safe component dependencies
- **Goals:** Build maintainable component-based UIs with automatic service injection; reduce boilerplate; maintain type safety

**API/Backend Developer** (28-45 years)
- **Role:** Backend engineer responsible for service architecture
- **Context:** Maintains service layer and wants clean integration with templating layer
- **Pain Points:** Template code often bypasses service layer abstractions; difficult to inject different implementations per request context; testing templates with mocked services is cumbersome
- **Goals:** Ensure templates respect service boundaries; enable context-aware service resolution; simplify testing with injectable mocks

**Library Maintainer** (30-50 years)
- **Role:** Open source maintainer or internal tools developer
- **Context:** Building reusable component libraries for internal teams or community
- **Pain Points:** Components need configurable dependencies; hard to provide different implementations per use case; users want flexibility without complexity
- **Goals:** Create flexible component APIs that support dependency injection; enable users to override component behavior; maintain backward compatibility

## The Problem

### Manual Service Wiring in Templates
Python web developers using template systems must manually pass services and dependencies through multiple component layers, leading to "prop drilling" where intermediate components receive props solely to pass them down. This creates tight coupling between components and their dependencies, making code harder to test, maintain, and refactor.

**Our Solution:** Automatic service injection using svcs container integration, where components declare their dependencies via type hints and receive them automatically at render time, without manual wiring.

### Limited Context-Aware Component Resolution
Modern web applications often need components to behave differently based on request context (multi-tenancy, A/B testing, feature flags, location-based rendering), but traditional templating systems lack built-in support for context-aware component selection.

**Our Solution:** Multi-implementation component resolution system (HopscotchInjector) that selects component implementations based on resources (tenant, feature flags) and location (URL paths), enabling dynamic component behavior without complex conditional logic in templates.

### Tight Coupling Between Templates and Business Logic
Templates often contain direct instantiation of services and business logic, making them difficult to test in isolation and creating dependencies that are hard to mock or replace during testing.

**Our Solution:** Clean separation through dependency injection layer, where templates depend only on abstract service interfaces, and concrete implementations are resolved by the svcs container, enabling easy testing with mock services.

## Differentiators

### Minimal Core, Powerful Extensions
Unlike monolithic template frameworks that bundle DI with templating, we provide a clean separation: tdom core remains minimal and dependency-free, while tdom-svcs adds optional DI capabilities. This allows developers to use tdom standalone or add DI only when needed, avoiding framework lock-in.

### Native Python 3.14 t-strings Integration
While other Python templating libraries use custom DSLs or require special syntax, tdom-svcs leverages Python 3.14's native t-strings (PEP 750), providing full IDE support, type checking, and Python syntax. This results in better developer experience with autocomplete, refactoring support, and compile-time error detection.

### Svcs-Based Architecture
Unlike custom DI implementations, we build on svcs by Hynek Schlawack, a battle-tested service container used in production by many Python projects. This provides proven reliability, excellent documentation, and integration with the broader Python ecosystem.

### Three-Layer Architecture
Unlike tightly coupled frameworks, tdom-svcs implements a clean three-layer architecture: (1) tdom core with minimal, upstreamable hooks, (2) tdom-svcs policy layer with svcs integration, and (3) svcs-di DI framework. This separation enables upstream contributions to tdom while maintaining flexibility for different DI strategies.

### Advanced Component Resolution Strategies
Unlike basic DI containers that only support simple lookup, tdom-svcs provides multiple injector implementations: DefaultInjector for basic DI, KeywordInjector for prop overrides, and HopscotchInjector for resource-based and location-based component resolution. This enables sophisticated multi-tenancy and feature flag scenarios without custom code.

## Key Features

### Core Features
- **Service Injection via svcs Container:** Components declare service dependencies through type hints and receive them automatically from the svcs container at render time, eliminating manual service wiring
- **Type-Safe Component Dependencies:** Full mypy and pyright support for component props and injected services, catching dependency errors at type-check time rather than runtime
- **Minimal tdom Core Changes:** Integration achieved through optional config/context parameters and pluggable hooks, keeping tdom core clean and suitable for upstreaming

### Component Resolution Features
- **Decorator-Based Component Discovery:** @Inject decorator marks injectable components and enables automatic discovery through package scanning
- **Keyword Override Support (KeywordInjector):** Template authors can override injected services with explicit kwargs, providing flexibility when needed without breaking DI patterns
- **Multi-Implementation Resolution (HopscotchInjector):** Select component implementations based on request resources (tenant ID, feature flags) and location (URL paths), enabling context-aware rendering

### Advanced Features
- **Pluggable Component Lifecycle Hooks:** Custom hooks for component initialization, service injection, and rendering phases, enabling middleware-like functionality for logging, validation, or transformation
- **Container Adapter Pattern:** Clean integration between tdom's component system and svcs container through adapter layer, isolating DI concerns from template rendering
- **Testing-Friendly Architecture:** Easy injection of mock services for testing, with clear boundaries between template components and service implementations
