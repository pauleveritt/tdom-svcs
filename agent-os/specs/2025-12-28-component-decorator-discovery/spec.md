# Specification: @injectable Decorator and Component Discovery

## Goal

Enable automatic component discovery and registration through package scanning, reusing svcs-di's @injectable decorator
to mark components and creating a scan_components() function that registers them in both ComponentNameRegistry and svcs
container.

## User Stories

- As a developer, I want to mark my component classes with @injectable so they can be automatically discovered and
  registered without manual registration calls
- As a developer, I want to call scan_components() at application startup to automatically discover and register all
  decorated components from specified packages

## Specific Requirements

**Reuse svcs-di's @injectable decorator directly**

- Import and re-export @injectable from svcs_di.injectors.decorators
- No wrapper or custom decorator needed
- Decorator supports bare syntax (@injectable) and parameterized syntax (@injectable(for_=X, resource=Y, location=Z))
- Decorator stores metadata on classes via __injectable_metadata__ attribute
- Only decoration-time validation is checking if applied to a class (not function)

**Validation for class-only decoration**

- Raise TypeError at decoration time if @injectable is applied to a function
- Error message should be clear: "The @injectable decorator can only be applied to classes, not functions"
- Check should happen in the decorator itself or in a wrapper function
- This prevents confusing errors later during scanning

**Create scan_components() function**

- Function signature: scan_components(registry: svcs.Registry, component_name_registry: ComponentNameRegistry, *
  packages: str | ModuleType)
- Leverages svcs-di's scan() function for package traversal and discovery
- Accepts multiple package names or module references
- Returns None (performs side effects by registering to both registries)

**Dual registration workflow**

- Call svcs-di's scan() to register decorated classes to svcs.Registry (type-based lookup)
- After scanning, iterate through discovered components and register each to ComponentNameRegistry
- Use class.__name__ as the string name key
- ComponentNameRegistry registration enables "Button" -> ButtonComponent type lookup
- svcs.Registry registration enables ButtonComponent -> instantiated instance with dependencies

**String name derivation from class name**

- Always use cls.__name__ as the string name for ComponentNameRegistry
- No override mechanism or custom name parameter
- Predictable mapping: ButtonComponent class -> "ButtonComponent" string name

**Package scanning leverages svcs-di infrastructure**

- Use svcs-di's _collect_modules_to_scan() for package resolution
- Use svcs-di's _discover_all_modules() for module discovery
- Use svcs-di's _collect_decorated_items() to find @injectable classes
- Reuse error handling patterns from svcs-di's scan()

**Error handling during scanning**

- Fail fast: If specified package doesn't exist or can't be imported, raise ImportError immediately
- Warn and continue: If individual module within package has import errors, log warning and continue
- Use Python's logging module with logger name "tdom_svcs.scanning"
- Error messages should include package/module name and original exception details

**Integration with existing ComponentLookup workflow**

- ComponentLookup.get_type() uses ComponentNameRegistry for string -> type resolution
- After getting type, ComponentLookup uses injector to construct instance
- Injector uses svcs container for type-based dependency resolution
- This creates two-stage resolution: name->type (ComponentNameRegistry), then type->instance (svcs)

**Support for resource and location-based registration**

- Components decorated with @injectable(resource=X) are registered with resource metadata
- Components decorated with @injectable(location=PurePath(...)) are registered with location metadata
- These are automatically handled by svcs-di's scan() function
- ComponentNameRegistry registration still happens regardless of resource/location metadata

**Thread-safe registration**

- ComponentNameRegistry.register() already uses threading.Lock
- svcs.Registry is thread-safe
- scan_components() should be called during single-threaded application startup
- No additional synchronization needed

## Usage Examples and Documentation

### Example 1: Basic Component with @injectable Decorator

```python
from dataclasses import dataclass
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from tdom import Tag

@injectable
@dataclass
class Button:
    """A button component with dependency injection."""
    label: str
    db: Inject[DatabaseService]  # Injected dependency

    def __call__(self) -> Tag:
        return t"<button>{self.label}</button>"
```

**Result:**
- Registered in ComponentNameRegistry as "Button" (string name)
- Registered in svcs.Registry as Button type
- Template usage: `t"<{Button} label='Click me' />"` resolves to Button instance with db injected

### Example 2: Component with Resource-Based Registration

```python
@injectable(resource=CustomerContext)
@dataclass
class CustomerDashboard:
    """Dashboard shown only for customer context."""
    user: Inject[UserService]
    analytics: Inject[AnalyticsService]

    def __call__(self) -> Tag:
        return t"<div>Customer Dashboard</div>"
```

**Result:**
- Registered in ComponentNameRegistry as "CustomerDashboard"
- Registered in svcs.Registry with resource metadata
- Resolved only in customer context

### Example 3: Component with Location-Based Registration

```python
from pathlib import PurePath

@injectable(location=PurePath("/admin"))
@dataclass
class AdminPanel:
    """Admin panel component for /admin routes."""
    auth: Inject[AuthService]

    def __call__(self) -> Tag:
        return t"<div>Admin Panel</div>"
```

**Result:**
- Registered in ComponentNameRegistry as "AdminPanel"
- Registered in svcs.Registry with location metadata
- Resolved only at /admin location

### Example 4: Using injectable() Directly (Without Decorator Syntax)

Sometimes you may need to apply the decorator programmatically rather than using decorator syntax:

```python
@dataclass
class Card:
    """A card component."""
    title: str
    content: str

    def __call__(self) -> Tag:
        return t"<div class='card'><h3>{self.title}</h3><p>{self.content}</p></div>"

# Apply decorator directly
Card = injectable(Card)
```

**When to use direct application:**
- Conditional decoration based on configuration
- Decorating classes from third-party libraries
- Dynamic component registration in plugins
- Testing scenarios where you want explicit control

### Example 5: Direct Application with Parameters

```python
# Apply decorator with parameters directly
CustomerCard = injectable(Card, resource=CustomerContext)
AdminCard = injectable(Card, resource=AdminContext)

# Now you have two variants of Card registered:
# - CustomerCard for customer context
# - AdminCard for admin context
```

**Result:**
- Both registered in ComponentNameRegistry ("CustomerCard", "AdminCard")
- Both registered in svcs.Registry with different resource metadata
- Single Card implementation, multiple registrations

### Example 6: Scanning and Registration

```python
import svcs
from tdom_svcs import ComponentNameRegistry, scan_components

# Setup
registry = svcs.Registry()
component_registry = ComponentNameRegistry()

# Scan packages for @injectable components
scan_components(
    registry,
    component_registry,
    "myapp.components",
    "myapp.widgets",
)

# Create container
container = svcs.Container(registry)

# Now components are discoverable by string name and type
```

### Example 7: Error - Decorator Applied to Function (Not Allowed)

```python
@injectable  # ❌ ERROR: Will raise TypeError
def my_button(label: str) -> Tag:
    return t"<button>{label}</button>"
```

**Error message:**
```
TypeError: The @injectable decorator can only be applied to classes, not functions.
```

**Solution:** Use a class-based component instead:
```python
@injectable  # ✓ Correct
@dataclass
class MyButton:
    label: str

    def __call__(self) -> Tag:
        return t"<button>{self.label}</button>"
```

## Visual Design

No visual assets provided.

## Existing Code to Leverage

**svcs-di's @injectable decorator**

- Located at /Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/decorators.py
- Provides dual syntax support (bare and parameterized)
- Stores metadata via __injectable_metadata__ attribute
- Supports for_, resource, and location parameters
- Reuse directly via import

**svcs-di's scan() function and helpers**

- Located at /Users/pauleveritt/projects/t-strings/svcs-di/src/svcs_di/injectors/locator.py starting line 1002
- Provides _collect_modules_to_scan() for package resolution
- Provides _discover_all_modules() for module discovery with error handling
- Provides _collect_decorated_items() to extract @injectable classes
- Provides _register_decorated_items() for svcs.Registry registration
- Reuse these internal functions or call scan() and then extract results

**ComponentNameRegistry.register() method**

- Located at
  /Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/services/component_registry/component_name_registry.py
- Thread-safe via threading.Lock
- Accepts name (str) and component_type (type or Callable)
- Already implemented and tested

**ComponentLookup service**

- Located at /Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/services/component_lookup/component_lookup.py
- Uses ComponentNameRegistry.get_type() for string->type resolution
- Uses KeywordInjector or KeywordAsyncInjector for instance construction
- Provides helpful error messages with suggestions via difflib
- Already integrated with tdom processor

**tdom-svcs module structure**

- Main exports in /Users/pauleveritt/projects/t-strings/tdom-svcs/src/tdom_svcs/__init__.py
- Service modules under tdom_svcs/services/
- Add new scanning module under tdom_svcs/ or tdom_svcs/scanning/

## Out of Scope

- Custom component name overrides (always use __name__)
- Creating a new decorator or wrapper around @injectable
- Automatic/lazy discovery without explicit scan_components() call
- Hot-reloading of components after scanning
- Advanced filtering or exclusion rules during package scanning
- Runtime validation of injectable dependencies before instantiation
- Function-based component support (only classes supported)
- Auto-scanning all imports without explicit package specification
- Caching or optimization of scanning results
- Support for undecorated components in scanning
