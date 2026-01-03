# Spec Requirements: Documentation

## Initial Description
[User's original spec description from raw-idea.md]

5 Documentation

## Requirements Discussion

### First Round Questions

**Q1:** Documentation Scope and Audience - I assume you want comprehensive documentation covering both beginner tutorials (getting started, basic DI patterns) and advanced guides (multi-tenancy, feature flags, middleware), along with a complete API reference generated from docstrings. Should we also include migration guides for teams moving from manual service wiring to tdom-svcs, or is that out of scope?

**Answer:** Don't do too much advanced guides, but certainly do middleware. Make a docs section about Services with pages for each service.

**Q2:** Documentation Structure - I'm thinking the docs should be organized as:
- Getting Started (installation, quickstart)
- Core Concepts (components, DI, registries)
- How-To Guides (common tasks)
- Advanced Topics (multi-implementation, resources, locations, middleware)
- API Reference (auto-generated)
- Examples Gallery (real-world patterns)

Does this structure align with your vision, or would you prefer a different organization?

**Answer:** [Not explicitly answered - assumes proposed structure is acceptable]

**Q3:** Example Coverage - I assume you want working examples for:
- Basic DI with class components
- Component discovery and scanning
- Resource-based resolution (multi-tenancy)
- Location-based resolution (URL-based components)
- Middleware usage
- Testing with mock services

Are there other specific use cases or patterns you want documented with examples?

**Answer:** Provide examples where a component is overridden by the "site" in the registry. Another example where it is overridden in just a particular case (resource, location). Make sure to have component examples that use `Inject[]`.

**Q4:** Interactive Documentation - Should we include executable code examples using Sphinx's doctest or Sybil (which is already in your tech stack) to ensure examples stay up-to-date and working? I notice you're already using MyST-Parser for Markdown support.

**Answer:** Use Sybil for cases where examples are in Markdown (but not in docstrings under `src`).

**Q5:** API Documentation Depth - I assume all public APIs should have comprehensive docstrings with Google/NumPy style formatting (since napoleon is configured). Should we also document internal APIs for contributors, or keep API docs focused on public interfaces only?

**Answer:** API docs don't have to be too in depth.

**Q6:** Diagrams and Visualizations - Should we include architecture diagrams showing the three-layer architecture (tdom core, tdom-svcs policy, svcs-di framework), component resolution flow, and injector selection decision trees? If yes, what format - Mermaid diagrams (currently commented out in conf.py), static images, or something else?

**Answer:** No diagrams.

**Q7:** Real-World Use Cases - The product mission mentions multi-tenancy, A/B testing, feature flags, and location-based rendering. Should the documentation include complete, production-ready examples for these scenarios, or are simplified educational examples sufficient?

**Answer:** Simplified educational examples.

**Q8:** Existing Documentation Treatment - I notice you have `docs/how_it_works.md` which is quite comprehensive, and several example folders with READMEs. Should we integrate and expand these into the new documentation structure, or start fresh with a new approach?

**Answer:** Integrate (and update it) - referring to docs/how_it_works.md.

**Q9:** Documentation Testing Strategy - Should all code examples in documentation be automatically tested (via Sybil or sphinx-doctest) to prevent documentation drift, or only certain sections? What's your tolerance for documentation build time vs. ensuring accuracy?

**Answer:** Just do Sybil for docs/*.

**Q10:** What should we explicitly NOT document? For example, should we exclude internal implementation details, experimental features, or keep the focus strictly on stable public APIs?

**Answer:** No explicit exclusions.

### Existing Code to Reference
[Based on user's response about similar features]

**Similar Features Identified:**
No specific similar features mentioned, but the following existing documentation and examples should be integrated:
- `docs/how_it_works.md` - Comprehensive guide to be updated and expanded
- `docs/index.md` - Current documentation homepage
- `examples/basic_tdom_svcs/` - Function component examples
- `examples/basic_tdom_injectable/` - Class component examples with @injectable
- `examples/component_discovery/` - Component scanning examples
- `examples/middleware/` - Comprehensive middleware examples (7 different scenarios)
- `examples/direct_decorator/` - Decorator usage examples
- `examples/resource_based_components.py` - Resource-based resolution
- `examples/location_based_components.py` - Location-based resolution

### Follow-up Questions

**Follow-up 1:** Services Documentation Structure - You mentioned making a docs section about Services with pages for each service. I can see three services in the codebase:
- `ComponentNameRegistry` (component_registry)
- `ComponentLookup` (component_lookup)
- `MiddlewareManager` (middleware)

Should each service get its own page covering setup, usage, API reference, and examples? Or would you prefer a different organization?

**Answer:** Yes - each service should get its own page covering setup, usage, API reference, and examples.

**Follow-up 2:** Component Override Examples - You requested examples showing:
- Component overridden by "site" in the registry (global override)
- Component overridden in particular case (resource/location)

Should these be standalone example files (like `examples/override_global.py` and `examples/override_resource.py`), or integrated into the documentation as inline Sybil-tested examples? Both?

**Answer:** Standalone - create example files like `examples/override_global.py` and `examples/override_resource.py`.

**Follow-up 3:** Existing Examples Integration - The existing examples are very comprehensive (especially middleware). Should we:
- Reference them from the docs with links and keep them separate?
- Extract key snippets into the docs as Sybil-tested examples?
- Or both - overview in docs with links to full examples?

**Answer:** Both - provide overview in docs with Sybil-tested snippets AND links to full examples.

**Follow-up 4:** how_it_works.md Updates - The existing `docs/how_it_works.md` is comprehensive but covers class vs function components, injector selection, etc. Should we:
- Keep it as a single comprehensive guide and add to it?
- Break it into multiple topic-based pages (Components, Injectors, Type Hinting, etc.)?
- Or reorganize it into the new structure you want?

**Answer:** Keep it as a single comprehensive guide and add to it.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
No visual assets to analyze.

## Requirements Summary

### Functional Requirements

#### Documentation Structure
- **Getting Started Section:**
  - Installation instructions (uv and pip)
  - Quickstart tutorial with basic DI example
  - Prerequisites (Python 3.14+, PEP 750 t-strings)

- **Core Concepts Section:**
  - Components (class vs function, when to use each)
  - Dependency injection with `Inject[]`
  - Service container basics
  - Component registries (ComponentNameRegistry)
  - Component lookup and resolution

- **How-To Guides Section:**
  - Update and expand existing `docs/how_it_works.md`
  - Keep as single comprehensive guide
  - Add middleware coverage
  - Add component override patterns
  - Add testing patterns

- **Services Section (NEW):**
  - Dedicated page for `ComponentNameRegistry` service
    - Setup instructions
    - Usage patterns
    - API reference
    - Examples
  - Dedicated page for `ComponentLookup` service
    - Setup instructions
    - Usage patterns
    - API reference
    - Examples
  - Dedicated page for `MiddlewareManager` service
    - Setup instructions
    - Usage patterns
    - API reference
    - Examples (with Sybil-tested snippets)

- **Examples Section:**
  - Overview of all examples with links to full code
  - Sybil-tested snippets demonstrating key patterns
  - Links to complete example files in `examples/` directory

- **API Reference Section:**
  - Auto-generated from docstrings (not too in-depth)
  - Public interfaces only
  - Google/NumPy style docstrings
  - Focus on essential usage information

#### New Example Files to Create
- `examples/override_global.py` - Component overridden by "site" in registry (global override)
- `examples/override_resource.py` - Component overridden for specific resource
- `examples/override_location.py` - Component overridden for specific location
- Ensure all new examples use components with `Inject[]` for dependency injection

#### Documentation Testing
- Sybil testing for all code examples in `docs/*.md` files
- No Sybil testing for docstrings under `src/`
- Ensure examples stay current and executable
- Configure in `docs/conftest.py`

#### Integration with Existing Content
- **Preserve and expand:** `docs/how_it_works.md`
- **Update:** `docs/index.md` with new structure
- **Reference:** All existing examples in `examples/` directory
- **Extract snippets:** Key patterns from examples for inline documentation
- **Provide links:** From docs to full example files

#### Documentation Format
- Markdown (MyST) for all documentation pages
- Furo theme (already configured)
- No diagrams required
- Code examples in Python with syntax highlighting
- Admonitions for tips, warnings, and notes

### Reusability Opportunities

**Existing Examples to Integrate:**
- `examples/basic_tdom_svcs/` - Educational function component pattern
- `examples/basic_tdom_injectable/` - Class components with @injectable
- `examples/component_discovery/` - Package scanning and registration
- `examples/middleware/` - 7 comprehensive middleware examples:
  - 01_basic_middleware.py
  - 02_middleware_with_dependencies.py
  - 03_testing_with_fakes.py
  - 04_manual_registration.py
  - 05_error_handling_middleware.py
  - 06_global_and_per_component.py
  - 07_async_middleware.py
- `examples/resource_based_components.py` - Multi-tenancy patterns
- `examples/location_based_components.py` - URL-based component resolution
- `examples/direct_decorator/` - Decorator usage

**Existing Documentation to Update:**
- `docs/how_it_works.md` - Expand with middleware and override patterns
- `docs/index.md` - Update with new navigation structure
- `docs/conf.py` - Already configured with Sphinx, MyST, Furo, Napoleon

**Tech Stack Already Configured:**
- Sphinx 8+ with Furo theme
- MyST-Parser for Markdown
- Sybil 8.4.2+ for documentation testing
- sphinx-autobuild for live reload
- Napoleon for docstring parsing (Google/NumPy styles)

### Scope Boundaries

**In Scope:**
- Comprehensive getting started guide
- Core concepts documentation
- Services documentation (3 dedicated pages)
- Middleware documentation (comprehensive with examples)
- Component override patterns (global, resource, location)
- Working code examples with Sybil testing
- API reference (auto-generated, not too deep)
- Integration with existing examples
- Updating `docs/how_it_works.md`
- Creating new override example files
- Sybil testing for `docs/*.md` files

**Out of Scope:**
- Advanced multi-tenancy production examples (use simplified educational examples)
- Advanced A/B testing examples
- Advanced feature flags examples
- Diagrams and visualizations (Mermaid or otherwise)
- Migration guides from manual service wiring
- Extensive advanced guides beyond middleware
- Internal API documentation for contributors
- Docstring testing under `src/` (no Sybil for source code)
- Documentation of experimental features

### Technical Considerations

**Documentation Technology:**
- Sphinx 8+ (already installed)
- MyST-Parser for Markdown (already configured)
- Furo theme (already configured)
- Sybil 8.4.2+ for testing docs examples
- sphinx-autobuild for development

**Testing Configuration:**
- Sybil testing only for `docs/**/*.md` files
- No testing for docstrings in `src/`
- Configure Sybil in `docs/conftest.py`
- Examples must be executable and current

**Existing Sphinx Extensions:**
- `myst_parser` - Markdown support
- `sphinx.ext.autodoc` - API documentation from docstrings
- `sphinx.ext.viewcode` - Links to source code
- `sphinx.ext.todo` - To-do items support
- `sphinx.ext.napoleon` - Google/NumPy docstrings

**File Organization:**
- `docs/index.md` - Homepage/navigation
- `docs/getting_started.md` - Installation and quickstart
- `docs/core_concepts.md` - Components, DI, registries
- `docs/how_it_works.md` - Comprehensive guide (update existing)
- `docs/services/component_registry.md` - ComponentNameRegistry service
- `docs/services/component_lookup.md` - ComponentLookup service
- `docs/services/middleware.md` - MiddlewareManager service
- `docs/examples.md` - Examples overview with snippets
- `docs/api_reference.md` - Auto-generated API docs
- `examples/override_global.py` - New example file
- `examples/override_resource.py` - New example file
- `examples/override_location.py` - New example file

**Integration Points:**
- Reference existing examples with links
- Extract key snippets for inline docs with Sybil
- Update existing `docs/how_it_works.md` rather than replace
- Use existing Sphinx configuration in `docs/conf.py`
- Follow existing docstring style (Google/NumPy via Napoleon)

**Key Patterns to Document:**
- Class components with `@injectable` and `Inject[]`
- Component discovery via `scan_components()`
- Global component overrides in registry
- Resource-based component overrides (multi-tenancy)
- Location-based component overrides (URL paths)
- Middleware setup and usage
- Testing with fakes (following svcs patterns)
- Service registration and container setup
