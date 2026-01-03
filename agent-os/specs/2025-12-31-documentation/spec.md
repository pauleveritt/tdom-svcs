# Specification: Documentation

## Goal
Create comprehensive documentation for tdom-svcs that guides users from installation to advanced patterns, with working examples and dedicated service pages, enabling developers to understand and effectively use dependency injection with TDOM components.

## User Stories
- As a new developer, I want clear installation and quickstart instructions so that I can start using tdom-svcs within minutes
- As a developer, I want detailed service documentation so that I understand how ComponentNameRegistry, ComponentLookup, and MiddlewareManager work
- As a developer implementing features, I want working code examples showing component override patterns (global, resource, location) so that I can implement multi-tenancy and context-aware components

## Specific Requirements

**Documentation Structure Update**
- Update docs/index.md with new toctree including getting_started, core_concepts, how_it_works, services section, examples, and api_reference
- Create docs/getting_started.md with installation instructions for both uv and pip, prerequisites noting Python 3.14+ and PEP 750 t-strings requirement, and quickstart with basic DI example
- Expand existing docs/how_it_works.md by adding middleware section, component override patterns section, and testing patterns section while keeping as single comprehensive guide
- Create docs/services/ directory for dedicated service pages
- Create docs/examples.md as overview page with Sybil-tested snippets and links to full example files

**Services Documentation Pages**
- Create docs/services/component_registry.md covering ComponentNameRegistry setup, registration API (register, get_type, get_all_names), thread safety, usage with scan_components, and code examples
- Create docs/services/component_lookup.md covering ComponentLookup setup, resolution workflow (registry lookup, middleware execution, injector selection, construction), error handling (ComponentNotFoundError, InjectorNotFoundError, RegistryNotSetupError), and code examples
- Create docs/services/middleware.md covering MiddlewareManager setup, middleware registration (direct instances and service types), execution workflow (priority ordering, halting), async support, Sybil-tested code snippets from examples/middleware/, and links to full examples

**New Example Files**
- Create examples/override_global.py demonstrating component overridden by site in registry with base component class, overridden component class using Inject[], registry setup showing override, and explanation comments
- Create examples/override_resource.py demonstrating component overridden for specific resource with base component, resource-specific override using Inject[], resource context classes, and HopscotchInjector resolution
- Create examples/override_location.py demonstrating component overridden for specific location with base component, location-specific override using Inject[], PurePath locations, and HopscotchInjector resolution

**API Reference Configuration**
- Create docs/api_reference.md with sphinx.ext.autodoc configuration, automodule directives for public modules (tdom_svcs, services.component_registry, services.component_lookup, services.middleware), and focus on public interfaces only

**Sybil Testing Configuration**
- Update docs/conftest.py if needed to ensure Sybil testing for all docs/*.md files using PythonCodeBlockParser
- Add necessary imports to conftest.py setup for common testing needs (svcs, dataclasses, tdom_svcs imports)
- Ensure examples in documentation are executable and tested
- Configure to skip docstrings under src/ (only test markdown files)

**Integration with Existing Examples**
- Reference all existing examples from docs/examples.md including basic_tdom_svcs, basic_tdom_injectable, component_discovery, middleware (all 7 examples), resource_based_components, location_based_components, and direct_decorator
- Extract key snippets from examples for inline documentation with Sybil testing
- Provide links from documentation to full example files in examples/ directory
- Add overview descriptions for each example category explaining the pattern demonstrated

**Documentation Format and Style**
- Use MyST Markdown for all documentation pages
- Include code examples with python syntax highlighting
- Use admonitions for tips, warnings, and important notes
- Keep API documentation concise and focused on essential usage
- Follow existing Google/NumPy docstring style in code
- Ensure all code examples demonstrate Inject[] usage in components

## Existing Code to Leverage

**ComponentNameRegistry service (src/tdom_svcs/services/component_registry/component_name_registry.py)**
- Thread-safe registry mapping string names to class types with register(), get_type(), and get_all_names() methods
- Validates that only class types can be registered
- Uses threading.Lock for free-threaded Python support
- Should be documented showing basic registration and retrieval patterns
- Reference docstrings for API documentation examples

**ComponentLookup service (src/tdom_svcs/services/component_lookup/component_lookup.py)**
- Bridges string names to component instances with full DI
- Workflow includes registry lookup, middleware execution, async detection, injector selection, and construction
- Uses HopscotchInjector for production with resource/location support
- Comprehensive error handling with custom exceptions
- Should be documented showing resolution workflow and error handling patterns

**MiddlewareManager service (src/tdom_svcs/services/middleware/middleware_manager.py)**
- Thread-safe middleware registration and execution
- Supports direct instances and service-based middleware
- Priority-ordered execution with halt support
- Async middleware detection and execution
- Should be documented with examples from examples/middleware/ directory

**scan_components function (src/tdom_svcs/scanning.py)**
- Comprehensive docstring explaining decorator usage, Inject[] parameters, package scanning, error handling, and migration guide
- Leverages svcs-di's scan infrastructure
- Dual registration to svcs.Registry and ComponentNameRegistry
- Should be referenced in getting_started and core_concepts documentation

**Existing documentation (docs/how_it_works.md)**
- Already comprehensive covering class vs function components, injector usage policy (HopscotchInjector vs KeywordInjector), type hinting approach, core architecture, Inject[] usage, advanced features (resource-based, location-based, async), and complete setup example
- Expand this with middleware and component override patterns sections rather than creating separate files
- Maintain single comprehensive guide structure

**Existing examples directory**
- examples/middleware/ with 7 comprehensive examples (01_basic to 07_async) demonstrating middleware patterns
- examples/resource_based_components.py showing resource-based registration with CustomerContext and AdminContext
- examples/location_based_components.py showing location-based registration with PurePath
- examples/component_discovery.py showing scan_components usage
- Reference these examples with links and extract key snippets for inline docs

**Existing Sphinx configuration (docs/conf.py)**
- Already configured with MyST-Parser, Furo theme, sphinx.ext.autodoc, sphinx.ext.napoleon, sphinx.ext.viewcode
- Sybil 8.4.2+ available for documentation testing
- No additional Sphinx configuration changes needed

**Existing conftest.py (docs/conftest.py)**
- Already configured with Sybil using PythonCodeBlockParser for markdown files
- May need to add common imports to setup function for doctests
- Pattern established for testing docs/*.md files

## Out of Scope
- Advanced multi-tenancy production examples beyond simplified educational examples
- Advanced A/B testing implementation examples
- Advanced feature flags implementation examples
- Diagrams and visualizations using Mermaid or other tools
- Migration guides from manual service wiring to tdom-svcs
- Extensive advanced guides beyond middleware documentation
- Internal API documentation for contributors and experimental features
- Documentation of internal implementation details not relevant to users
- Sybil testing for docstrings under src/ directory
- Interactive documentation examples beyond standard code blocks
