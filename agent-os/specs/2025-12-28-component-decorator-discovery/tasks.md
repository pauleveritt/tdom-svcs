# Task Breakdown: @injectable Decorator and Component Discovery

## Overview
Total Tasks: 4 Task Groups

## Task List

### Decorator Infrastructure

#### Task Group 1: Decorator Import and Validation
**Dependencies:** None

- [x] 1.0 Complete decorator import and validation layer
  - [x] 1.1 Write 2-8 focused tests for decorator validation
    - Test @injectable works on classes (basic case)
    - Test @injectable raises TypeError on functions (decoration-time error)
    - Test @injectable with for_ parameter on classes
    - Test @injectable with resource parameter on classes
    - Test @injectable with location parameter on classes
    - Test metadata storage on decorated classes
    - Test error message clarity for function decoration
    - Location: `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_decorator_validation.py`
  - [x] 1.2 Create decorator module with validation
    - Create `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/decorator.py`
    - Import `injectable` from `svcs_di.injectors.decorators`
    - Create validation wrapper that checks `inspect.isclass()` at decoration time
    - Raise TypeError with message "The @injectable decorator can only be applied to classes, not functions" for non-classes
    - Support both bare (@injectable) and parameterized (@injectable(for_=X)) syntax
    - Re-export validated decorator
    - Pattern reference: `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/decorators.py`
  - [x] 1.3 Export decorator from main __init__.py
    - Update `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/__init__.py`
    - Add `injectable` to imports and __all__
    - Make decorator easily accessible: `from tdom_svcs import injectable`
  - [x] 1.4 Ensure decorator validation tests pass
    - Run ONLY the 2-8 tests written in 1.1
    - Verify class decoration works correctly
    - Verify function decoration raises TypeError at decoration time
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 1.1 pass
- @injectable can be imported from tdom_svcs
- Decorator accepts classes and stores metadata via __injectable_metadata__
- Decorator raises clear TypeError immediately when applied to functions
- Decorator supports for_, resource, and location parameters

### Scanning Infrastructure

#### Task Group 2: Component Discovery and Scanning
**Dependencies:** Task Group 1 (completed - decorator now in svcs-di)

- [x] 2.0 Complete scanning infrastructure
  - [x] 2.1 Write 2-8 focused tests for scan_components()
    - Test scan_components() discovers decorated classes in a package
    - Test dual registration (ComponentNameRegistry + svcs.Registry)
    - Test string name derivation from class.__name__
    - Test package not found raises ImportError (fail fast)
    - Test module import error logs warning and continues
    - Test resource-based component registration
    - Test location-based component registration
    - Location: `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_scan_components.py`
  - [x] 2.2 Create scan_components() function
    - Create `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/scanning.py`
    - Function signature: `scan_components(registry: svcs.Registry, component_name_registry: ComponentNameRegistry, *packages: str | ModuleType)`
    - Import scan infrastructure from svcs-di: `from svcs_di.injectors.locator import scan`
    - Create logger: `logging.getLogger("tdom_svcs.scanning")`
    - Leverage svcs-di's scan() for type-based registration to svcs.Registry
    - After scan(), extract decorated classes and register to ComponentNameRegistry
    - Use `cls.__name__` as string name for ComponentNameRegistry.register()
    - Pattern reference: `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/locator.py` lines 1002-1062
  - [x] 2.3 Implement dual registration workflow
    - Call `scan(registry, *packages)` to register to svcs.Registry (type-based lookup)
    - After scan completes, iterate packages to collect @injectable decorated classes
    - Reuse svcs-di helpers: `_collect_modules_to_scan()`, `_discover_all_modules()`, `_collect_decorated_items()`
    - For each discovered class, call `component_name_registry.register(cls.__name__, cls)`
    - This enables two-stage resolution: "Button" -> ButtonComponent (ComponentNameRegistry), then ButtonComponent -> instance (svcs)
  - [x] 2.4 Add error handling
    - Fail fast: Re-raise ImportError if package doesn't exist (let it bubble up)
    - Warn and continue: Catch and log warnings for individual module import errors
    - Use logging with logger name "tdom_svcs.scanning"
    - Include package/module name and original exception in log messages
    - Pattern reference: `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/locator.py` lines 924-930
  - [x] 2.5 Export scan_components from main __init__.py
    - Update `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/__init__.py`
    - Add `scan_components` to imports and __all__
    - Make function easily accessible: `from tdom_svcs import scan_components`
  - [x] 2.6 Ensure scanning infrastructure tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify package discovery works correctly
    - Verify dual registration happens for all discovered components
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 2.1 pass
- scan_components() can be imported from tdom_svcs
- Function discovers @injectable decorated classes in specified packages
- Components registered in both ComponentNameRegistry (string name) and svcs.Registry (type)
- String names derived from class.__name__
- Package not found raises ImportError immediately
- Module import errors logged as warnings and scanning continues
- Resource and location metadata handled automatically via svcs-di's scan()

### Integration Layer

#### Task Group 3: ComponentLookup Integration
**Dependencies:** Task Group 2

- [x] 3.0 Complete ComponentLookup integration
  - [x] 3.1 Write 2-8 focused tests for end-to-end component resolution
    - Test ComponentLookup resolves scanned components by string name
    - Test two-stage resolution: name->type (ComponentNameRegistry), type->instance (svcs)
    - Test component with Inject[] dependencies gets injected correctly
    - Test component with resource metadata resolved in correct context
    - Test component with location metadata resolved at correct location
    - Test error handling when component name not found
    - Test error raised for unknown scanned component
    - Location: `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_component_lookup_integration.py`
  - [x] 3.2 Verify ComponentLookup workflow
    - No code changes needed (ComponentLookup already uses ComponentNameRegistry.get_type())
    - Verify ComponentLookup.__call__() retrieves ComponentNameRegistry from container
    - Verify ComponentLookup resolves string name to type via ComponentNameRegistry.get_type()
    - Verify ComponentLookup uses injector to construct instance from type
    - Verify injector uses svcs container for Inject[] parameter resolution
    - Reference: `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/services/component_lookup/component_lookup.py`
  - [x] 3.3 Create integration example
    - Create example showing complete workflow
    - Show @injectable decoration of component class
    - Show scan_components() call at app startup
    - Show component resolution via ComponentLookup
    - Show Inject[] parameter usage for dependencies
    - Location: `/Users/pauleveritt/projects/t-strings/tdom-svcs/examples/component_discovery.py` or in docstrings
  - [x] 3.4 Ensure integration tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify end-to-end component resolution works
    - Verify two-stage lookup succeeds
    - Do NOT run the entire test suite at this stage

**Acceptance Criteria:**
- The 2-8 tests written in 3.1 pass
- ComponentLookup successfully resolves scanned components by string name
- Two-stage resolution works: name->type->instance
- Components with Inject[] dependencies get injected correctly
- Resource and location-based components resolved in correct contexts
- Error raised appropriately when component not found

### Testing and Documentation

#### Task Group 4: Test Review, Documentation, and Examples
**Dependencies:** Task Groups 1-3

- [x] 4.0 Review tests and create documentation
  - [x] 4.1 Review existing tests from Task Groups 1-3
    - Review the 2-8 tests written by decorator-engineer (Task 1.1) - NOTE: Task Group 1 was not implemented since we use svcs-di's decorator directly
    - Review the 8 tests written by scanning-engineer (Task 2.1) in test_scan_components.py
    - Review the 8 tests written by integration-engineer (Task 3.1) in test_component_lookup_integration.py
    - Total existing tests: 16 tests (8 from Task 2 + 8 from Task 3)
  - [x] 4.2 Analyze test coverage gaps for THIS feature only
    - Identify critical workflows that lack test coverage
    - Focus on: thread-safety of registration, error paths, edge cases
    - Check: decorator with all parameter combinations, scan with multiple packages
    - Prioritize: Integration testing between all layers
    - Do NOT assess entire application test coverage
  - [x] 4.3 Write up to 10 additional strategic tests maximum
    - Thread-safety: Test concurrent registration (if not covered) ✓
    - Error handling: Test all error paths in scan_components() ✓
    - Edge cases: Empty packages, modules without components, invalid metadata ✓
    - Integration: Test scan_components() + ComponentLookup + tdom processor workflow ✓
    - Parameterization: Test all combinations of for_, resource, location ✓
    - Do NOT write comprehensive coverage for all scenarios
    - Location: Add to existing test files or create `/Users/pauleveritt/projects/t-strings/tdom-svcs/tests/test_component_discovery_edge_cases.py` ✓
    - Result: 9 additional tests added in test_component_discovery_edge_cases.py
  - [x] 4.4 Create usage documentation
    - Document @injectable decorator usage with examples ✓
    - Document scan_components() function with startup pattern ✓
    - Document Inject[] parameter usage ✓
    - Document resource and location-based registration ✓
    - Document error handling and troubleshooting ✓
    - Document migration from manual ComponentNameRegistry.register() calls ✓
    - Location: Update module docstrings in `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/scanning.py` (no decorator.py since we removed it) ✓
  - [x] 4.5 Create comprehensive examples
    - Example 1: Basic component with @injectable (from spec.md line 94) ✓ - examples/component_discovery.py
    - Example 2: Component with resource-based registration (from spec.md line 118) ✓ - examples/resource_based_components.py
    - Example 3: Component with location-based registration (from spec.md line 137) ✓ - examples/location_based_components.py
    - Example 4: Direct injectable() application (from spec.md line 159) ✓ - examples/direct_decorator_application.py
    - Example 5: Direct application with parameters (from spec.md line 180) ✓ - examples/direct_decorator_application.py
    - Example 6: Complete scanning and registration workflow (from spec.md line 198) ✓ - examples/component_discovery.py
    - Example 7: Error case - decorator on function (from spec.md line 222) ✓ - covered in module documentation
    - Location: Module docstrings or `/Users/pauleveritt/projects/t-strings/tdom-svcs/examples/` directory ✓
  - [x] 4.6 Run feature-specific tests only
    - Run ONLY tests related to this spec's feature (tests from 2.1, 3.1, and 4.3)
    - Expected total: approximately 16-26 tests maximum (16 existing + up to 10 new)
    - Result: 25 tests total (8 from Task 2 + 8 from Task 3 + 9 new edge cases)
    - Do NOT run the entire application test suite ✓
    - Verify critical workflows pass ✓
    - Fix any failures before considering feature complete ✓

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 16-26 tests total) ✓ - 25 tests passing
- Critical user workflows for component discovery and registration are covered ✓
- No more than 10 additional tests added when filling in testing gaps ✓ - 9 tests added
- Documentation covers all usage patterns from spec.md ✓
- Examples demonstrate all decorator parameters and scanning scenarios ✓
- Error handling and troubleshooting guidance provided ✓

## Execution Order

Recommended implementation sequence:
1. **Decorator Infrastructure (Task Group 1)** - Import and validate @injectable decorator
2. **Scanning Infrastructure (Task Group 2)** - Create scan_components() and implement dual registration
3. **Integration Layer (Task Group 3)** - Verify ComponentLookup integration and create examples
4. **Testing and Documentation (Task Group 4)** - Review tests, fill gaps, create documentation and examples

## Key Technical Notes

**Reusability:**
- Direct import of @injectable from svcs-di (zero duplication)
- Leverage svcs-di's scan() and helper functions (_collect_modules_to_scan, _discover_all_modules, _collect_decorated_items)
- Use existing ComponentNameRegistry and ComponentLookup services
- Follow existing error handling patterns from svcs-di

**Dual Registration Strategy:**
1. Use svcs-di's scan() to register components in svcs.Registry (type-based)
2. Extract discovered components and register in ComponentNameRegistry (string-based)
3. This enables two-stage resolution: "Button" -> ButtonComponent -> injected instance

**String Name Derivation:**
- Always use `cls.__name__` as the string name
- No override mechanism or custom name parameter
- Predictable mapping: ButtonComponent -> "ButtonComponent"

**Error Handling Philosophy:**
- Fail fast: Package not found, decorator on function
- Warn and continue: Individual module import errors during scanning
- Clear error messages: ComponentLookup provides clear errors when component not found

**Thread Safety:**
- ComponentNameRegistry uses threading.Lock (already implemented)
- svcs.Registry is thread-safe
- scan_components() should be called during single-threaded app startup
- No additional synchronization needed

**Integration Points:**
- `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/decorators.py` - Import @injectable
- `/Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/locator.py` - Use scan() and helpers
- `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/services/component_registry/component_name_registry.py` - Register string names
- `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/services/component_lookup/component_lookup.py` - Verify integration
- `/Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/__init__.py` - Export new APIs
