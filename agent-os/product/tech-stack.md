# Tech Stack

## Framework & Runtime
- **Language/Runtime:** Python 3.14+ (requires PEP 750 t-strings and PEP 695 generics)
- **Package Manager:** uv (modern Python package manager)
- **Build System:** uv_build

## Core Dependencies
- **tdom:** Template DOM library for Python 3.14 t-strings (workspace dependency)
- **svcs:** Service container by Hynek Schlawack for dependency management
- **svcs-di:** Dependency injection layer providing auto(), Inject[T] (workspace dependency)

## Testing & Quality
- **Test Framework:** pytest with plugins:
  - pytest-cov for coverage reporting (7.13.0+)
  - pytest-xdist for parallel test execution (3.8.0+)
  - pytest-run-parallel for concurrent test runs (0.8.1+)
  - pytest-timeout for detecting hangs/deadlocks (2.4.0+)
  - sybil for documentation testing (8.4.2+)
- **Type Checking:**
  - mypy (via pyrefly 0.46.1+)
  - pyright (1.1.407+)
  - ty for runtime type utilities (0.0.6+)
- **Linting/Formatting:** ruff (0.14.10+)
- **Coverage:** coverage.py (7.13.0+)

## Documentation
- **Documentation Generator:** Sphinx (8+)
- **Documentation Theme:** Furo (2025.12.19+)
- **Markdown Parser:** MyST-Parser for Markdown support in Sphinx
- **Live Reload:** sphinx-autobuild (2025.8.25+)
- **Markdown Enhancements:** linkify-it-py (2.0.3+)

## Development Tools
- **Task Runner:** Just (justfile-based task automation)
- **Workspace Management:** uv workspace (monorepo with tdom, svcs-di, tdom-svcs)

## Testing Configuration
- **Test Paths:** tests/, src/, docs/
- **Test Discovery:** test_*.py files
- **Test Markers:**
  - `slow`: marks tests as slow (excluded by default)
  - `freethreaded`: marks tests verifying free-threading compatibility
- **Timeouts:**
  - Test timeout: 60 seconds
  - Faulthandler timeout: 120 seconds (for detecting deadlocks in free-threaded mode)
- **Python Path:** examples/ directory added to PYTHONPATH for example imports

## Architecture Layers
1. **tdom (core):** Minimal templating library with optional hooks (upstreamable)
2. **tdom-svcs (policy):** svcs container integration and injector configurations
3. **svcs-di (framework):** Dependency injection primitives (auto(), Inject[T], injectors)

## Deployment & Distribution
- **Package Distribution:** PyPI
- **Version:** 0.1.0 (Alpha)
- **Python Version Support:** 3.14+ only (requires t-strings)
- **Typing:** Fully typed package (py.typed marker)

## Quality Standards
- **Type Safety:** 100% type coverage with mypy and pyright
- **Code Style:** ruff with strict linting rules
- **Free-Threading Safety:** Tests verify compatibility with Python 3.14 free-threaded mode
- **Test Coverage:** Comprehensive coverage with pytest-cov
- **Documentation Testing:** Sybil ensures code examples in docs are correct and up-to-date
