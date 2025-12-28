---
name: services
description: Guide for working with services using svcs library, with optional svcs-di for automatic dependency injection
version: 3.1.0
tags: [svcs, svcs-di, dependency-injection, testing, architecture, inject, injectable]
---

# Working with Services in svcs

## What is a Service?

A **service** is a local object managed by svcs that provides **behavior without business-relevant state**. Services are "infrastructure doers" - they provide capabilities (database access, API clients, configuration) but don't make business decisions.

**Key principle**: Services pass data back and forth; the domain model decides what happens next.

**Common examples**:
- Database connections
- HTTP/API clients
- Cache systems
- File handlers
- Configuration objects
- External service clients

## Creating a Service

### Manual Registration (No Dependency Injection)

Define a service and register it manually:

```python
from dataclasses import dataclass
import svcs

@dataclass(frozen=True)
class DatabaseService:
    """Service that provides database access."""
    host: str = "localhost"
    port: int = 5432
    
    def connect(self):
        """Connect to database."""
        return f"Connected to {self.host}:{self.port}"

# Create registry and register
registry = svcs.Registry()
registry.register_value(DatabaseService, DatabaseService())

# Get service from container
container = svcs.Container(registry)
db = container.get(DatabaseService)
```

### With svcs-di Automatic Injection

Use `Inject[T]` to mark dependencies and `auto()` to create factory:

```python
from dataclasses import dataclass
import svcs
from svcs_di import Inject, auto

@dataclass
class DatabaseService:
    """Service that provides database access."""
    host: str = "localhost"
    port: int = 5432

@dataclass
class CacheService:
    """Service that depends on database."""
    db: Inject[DatabaseService]  # Automatically injected!
    ttl: int = 300

# Register both services
registry = svcs.Registry()
registry.register_factory(DatabaseService, DatabaseService)
registry.register_factory(CacheService, auto(CacheService))

# Get service - dependencies auto-resolved
container = svcs.Container(registry)
cache = container.get(CacheService)
# cache.db is automatically a DatabaseService instance!
```

**How `Inject[T]` works**:
1. `Inject[DatabaseService]` marks the field for auto-injection
2. `auto(CacheService)` wraps the class to resolve `Inject` fields
3. When `container.get(CacheService)` is called:
   - The auto-generated factory looks for `Inject[T]` fields
   - For each one, it calls `container.get(T)` to resolve the dependency
   - Returns fully constructed instance with all dependencies

**Key benefits**:
- No manual factory functions needed
- Type-safe dependency resolution
- Explicit opt-in (only `Inject[T]` fields are injected)
- Works with dataclasses and regular callables

### With @injectable Decorator (Auto-Discovery)

Use `@injectable` to mark services for automatic discovery and registration:

```python
from dataclasses import dataclass
import svcs
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import scan

@injectable
@dataclass
class DatabaseService:
    """Service that provides database access."""
    host: str = "localhost"
    port: int = 5432

@injectable
@dataclass
class CacheService:
    """Service that depends on database."""
    db: Inject[DatabaseService]  # Automatically injected!
    ttl: int = 300

# Auto-discover and register all @injectable services
registry = svcs.Registry()
scan(registry)  # Finds all @injectable classes and registers them

# Get service - everything auto-wired
container = svcs.Container(registry)
cache = container.get(CacheService)
```

**Benefits of @injectable**:
- No manual registration boilerplate
- Just mark classes with `@injectable` and call `scan()`
- Supports resource-based and location-based registration
- Works seamlessly with `Inject[T]` dependency injection

**When to use**:
- Large applications with many services
- When you want convention-over-configuration
- Plugin architectures with auto-discovery

### With Protocols (Interface-Based)

Use protocols for interface-based dependency injection:

```python
from typing import Protocol
from dataclasses import dataclass
import svcs
from svcs_di import Inject, auto

class Greeting(Protocol):
    """Protocol for greeting services."""
    def greet(self, name: str) -> str: ...

@dataclass
class DefaultGreeting:
    """Default implementation."""
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"

@dataclass
class WelcomeService:
    """Service that depends on Greeting protocol."""
    greeting: Inject[Greeting]  # Protocol, not concrete type!

# Register implementation for protocol
registry = svcs.Registry()
registry.register_factory(Greeting, DefaultGreeting)
registry.register_factory(WelcomeService, auto(WelcomeService))

# auto() automatically uses get_abstract() for protocols
container = svcs.Container(registry)
service = container.get(WelcomeService)
```
## Creating Services: Directory Structure Pattern

For larger projects with many services, use a structured directory layout, under a `services/` directory:

### Directory Structure

```
services/
├── database/
│   ├── __init__.py          # Export protocol and implementation
│   ├── models.py            # Protocol definition
│   └── implementation.py    # Concrete implementation
├── cache/
│   ├── __init__.py
│   ├── models.py
│   └── redis_impl.py
└── ...
```

### 1. Define Protocol (models.py)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable  # Allows isinstance() checks
class DatabaseProtocol(Protocol):
    """Protocol defining database service interface."""

    def connect(self) -> None:
        """Establish database connection."""
        ...

    def query(self, sql: str) -> list[dict]:
        """Execute query and return results."""
        ...
```

**Key points**:
- Use `@runtime_checkable` decorator for runtime type checking
- Define clear interface with type hints
- Document expected behavior in docstrings

### 2. Implement Service (implementation.py)

```python
from dataclasses import dataclass
from .models import DatabaseProtocol

@dataclass(frozen=True)
class PostgresDatabase:
    """PostgreSQL implementation of DatabaseProtocol."""

    host: str
    port: int
    database: str

    def connect(self) -> None:
        """Establish PostgreSQL connection."""
        # Implementation here
        pass

    def query(self, sql: str) -> list[dict]:
        """Execute PostgreSQL query."""
        # Implementation here
        return []
```

**Key points**:
- Use `@dataclass(frozen=True)` for immutability
- Implement all protocol methods
- Keep implementation focused on infrastructure, not business logic

### 3. Export from __init__.py

```python
from .models import DatabaseProtocol
from .implementation import PostgresDatabase

__all__ = ["DatabaseProtocol", "PostgresDatabase"]
```

### 4. Register Service

```python
import svcs
from services.database import DatabaseProtocol, PostgresDatabase

# Manual registration
registry = svcs.Registry()
registry.register_factory(
    DatabaseProtocol,
    lambda: PostgresDatabase(host="prod", port=5432, database="mydb")
)

# Or with @injectable for auto-discovery
from svcs_di.injectors.decorators import injectable

@injectable(for_=DatabaseProtocol)
@dataclass(frozen=True)
class PostgresDatabase:
    ...
```

### 5. Services That Depend on svcs.Container

Many services need access to the svcs.Container to resolve other services dynamically. This is a common pattern for adapter/lookup services.

**Pattern: Accept svcs.Container in the service**

```python
from dataclasses import dataclass
from typing import Protocol, runtime_checkable
import svcs

@runtime_checkable
class ComponentLookupProtocol(Protocol):
    """Protocol for services that need container access."""

    def __init__(self, container: svcs.Container) -> None:
        """
        Initialize with svcs.Container.

        Args:
            container: svcs.Container that holds service registrations
        """
        ...

    def resolve(self, name: str) -> object | None:
        """Resolve a service by name."""
        ...

@dataclass
class ComponentLookup:
    """Service that uses container to resolve other services."""

    container: svcs.Container  # Type as svcs.Container, not Any

    def resolve(self, name: str) -> object | None:
        """Resolve a service dynamically from the container."""
        try:
            return self.container.get(SomeService)
        except svcs.ServiceNotFoundError:
            return None
```

**Key points**:
- Type the `container` parameter as `svcs.Container`, not `Any`
- Include this in both the protocol and implementation
- The container gives access to all registered services
- Use `container.get(ServiceType)` to resolve dependencies dynamically
- This pattern is common for adapters, lookups, and orchestrators

**When to use**:
- Services that need to resolve dependencies dynamically (not at initialization)
- Adapter services that bridge between different systems
- Lookup/registry services that resolve by name or other criteria
- Orchestrator services that coordinate multiple services

## Testing Services: Best Practices

### Principle: Use Fakes, Not Mocks

Create simple, predictable test doubles that implement the protocol:

```python
from dataclasses import dataclass
from services.database import DatabaseProtocol

@dataclass
class FakeDatabase:
    """Fake database for testing - predictable, no side effects."""

    _query_results: dict[str, list[dict]]

    def connect(self) -> None:
        """No-op connection for testing."""
        pass

    def query(self, sql: str) -> list[dict]:
        """Return pre-configured results."""
        return self._query_results.get(sql, [])

def test_service_with_fake():
    """Test service using fake database."""
    # Setup fake with known data
    fake_db = FakeDatabase(
        _query_results={
            "SELECT * FROM users": [{"id": 1, "name": "Alice"}]
        }
    )

    # Create service with fake (no svcs needed in test!)
    service = MyService(db=fake_db)

    # Test behavior
    users = service.get_users()
    assert len(users) == 1
    assert users[0]["name"] == "Alice"
```

**Why fakes over mocks**:
- Simple to understand and maintain
- No mock framework magic
- Tests are more resilient to refactoring
- Follows the dependency chain naturally

### Testing Protocol Conformance

Verify implementations conform to the protocol:

```python
import pytest
from services.database import DatabaseProtocol, PostgresDatabase

def test_postgres_implements_protocol():
    """Verify PostgresDatabase conforms to DatabaseProtocol."""
    db = PostgresDatabase(host="test", port=5432, database="test")

    # runtime_checkable allows isinstance check
    assert isinstance(db, DatabaseProtocol)

    # Verify all protocol methods exist
    assert hasattr(db, "connect")
    assert hasattr(db, "query")
    assert callable(db.connect)
    assert callable(db.query)
```

### Testing with Dependency Injection

When testing services that use `Inject[T]`, register fakes in test registry:

```python
import svcs
from svcs_di import Inject, auto
from dataclasses import dataclass

@dataclass
class CacheService:
    db: Inject[DatabaseProtocol]
    ttl: int = 300

def test_cache_with_fake_db():
    """Test CacheService with fake database."""
    # Create test registry
    registry = svcs.Registry()

    # Register fake
    fake_db = FakeDatabase(_query_results={})
    registry.register_value(DatabaseProtocol, fake_db)

    # Register service under test
    registry.register_factory(CacheService, auto(CacheService))

    # Get service - fake is injected
    container = svcs.Container(registry)
    cache = container.get(CacheService)

    # Verify fake was injected
    assert cache.db is fake_db
    assert isinstance(cache.db, FakeDatabase)
```

### Testing Guidelines

✅ **DO**:
- Create fakes that implement the protocol
- Make fakes simple and predictable
- Pass fakes directly to service constructors when possible
- Use `@runtime_checkable` on protocols for isinstance checks
- Test protocol conformance separately from behavior
- Keep test data minimal and focused

❌ **DON'T**:
- Use mock frameworks unless absolutely necessary
- Create complex fakes with lots of state
- Test svcs container mechanics in business logic tests
- Couple tests tightly to svcs implementation details
- Mock the service under test itself


## Registering Services

### Registration Methods

```python
import svcs
from svcs_di import auto

# Register as value (pre-created singleton)
db_instance = DatabaseService(host="prod", port=5432)
registry.register_value(DatabaseService, db_instance)

# Register as factory (created on-demand)
registry.register_factory(DatabaseService, lambda: DatabaseService())

# Register with auto() for dependency injection
registry.register_factory(CacheService, auto(CacheService))

# Or use @injectable decorator and scan()
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import scan

scan(registry)  # Auto-registers all @injectable classes
```

**Value vs Factory vs @injectable**:
- **`register_value()`**: Pre-created singleton, used immediately
- **`register_factory()`**: Created lazily when first requested via `container.get()`
- **`auto()`**: Wraps a type/callable to auto-inject `Inject[T]` dependencies
- **`@injectable` + `scan()`**: Auto-discovery and registration via decorator

### Resolution Precedence

When using `auto()` with `DefaultInjector`, values are resolved with two-tier precedence:
1. **Container services**: `container.get(T)` or `container.get_abstract(T)` for `Inject[T]` fields
2. **Default values**: From parameter/field definition (e.g., `ttl: int = 300`)

```python
from dataclasses import dataclass
import svcs
from svcs_di import Inject, auto

@dataclass
class Service:
    db: Inject[Database]      # Resolved from container
    timeout: int = 30          # Uses default value
    cache: Inject[Cache]       # Resolved from container

# timeout gets default 30, db and cache come from container
registry = svcs.Registry()
registry.register_factory(Database, Database)
registry.register_factory(Cache, Cache)
registry.register_factory(Service, auto(Service))
```

## Using Services

### Basic Usage

```python
import svcs
from svcs_di import auto

# Create registry and register services
registry = svcs.Registry()
registry.register_factory(DatabaseService, DatabaseService)
registry.register_factory(CacheService, auto(CacheService))

# Create container and get services
container = svcs.Container(registry)
cache = container.get(CacheService)

# Use the service (behavior only)
result = cache.get_from_cache("key")
```

### In Application Code

Typical pattern in web applications:

```python
import svcs

def my_view(request):
    """View function that uses services."""
    # Get container from request (framework-specific)
    container = svcs_from(request)
    
    # Get services
    db = container.get(DatabaseService)
    cache = container.get(CacheService)
    
    # Use services to get data
    data = cache.get_or_compute("key", lambda: db.query(...))
    
    return {"data": data}
```

## Testing Services

### Principle: Use Fakes, Not Mocks

Create simple test doubles that implement the same interface:

```python
from dataclasses import dataclass

def test_service_behavior():
    """Test service using simple fake objects."""
    # Create fake dependencies
    fake_db = DatabaseService(host="test", port=1234)
    
    # Create service directly with fake
    service = CacheService(db=fake_db, ttl=60)
    
    # Test behavior
    assert service.db.host == "test"
    assert service.ttl == 60
```

### Testing with Dependency Injection

Test services that use `Inject[T]` by registering test doubles:

```python
import svcs
from svcs_di import auto

def test_service_with_injection():
    """Test service with auto-injected dependencies."""
    # Create test registry with fake services
    registry = svcs.Registry()
    
    # Register fake database
    fake_db = DatabaseService(host="test", port=1234)
    registry.register_value(DatabaseService, fake_db)
    
    # Register service with auto() as usual
    registry.register_factory(CacheService, auto(CacheService))
    
    # Get service - fake DB is auto-injected
    container = svcs.Container(registry)
    service = container.get(CacheService)
    
    assert service.db.host == "test"
    assert service.db is fake_db
```

### Testing Service Registration

```python
import svcs

def test_service_registered():
    """Verify service is registered correctly."""
    registry = svcs.Registry()
    registry.register_factory(DatabaseService, DatabaseService)
    
    # Verify it's in the registry
    assert DatabaseService in registry
    
    # Verify it can be retrieved
    container = svcs.Container(registry)
    db = container.get(DatabaseService)
    assert isinstance(db, DatabaseService)
```

### Testing with Protocol Fakes

When using protocols, create simple fakes that match the protocol:

```python
from dataclasses import dataclass
import svcs
from svcs_di import auto

@dataclass
class FakeGreeting:
    """Fake greeting for testing."""
    def greet(self, name: str) -> str:
        return f"Test: {name}"

def test_with_protocol():
    """Test service that depends on protocol."""
    registry = svcs.Registry()
    
    # Register fake implementation
    registry.register_value(Greeting, FakeGreeting())
    registry.register_factory(WelcomeService, auto(WelcomeService))
    
    container = svcs.Container(registry)
    service = container.get(WelcomeService)
    
    assert service.greeting.greet("World") == "Test: World"
```

## Service Lifecycle

### Registry (Application-Scoped)

- Lives for the entire application lifetime
- Stores factory functions and values
- Shared across all containers
- One per application

```python
import svcs

# Create once at application startup
registry = svcs.Registry()
# Register all services
registry.register_factory(DatabaseService, DatabaseService)
registry.register_factory(CacheService, auto(CacheService))
```

### Container (Request-Scoped)

- Lives for a single request/operation
- Creates and caches service instances
- Handles cleanup when closed
- Many per application

```python
import svcs

# Create per request
container = svcs.Container(registry)

# Use services
db = container.get(DatabaseService)
cache = container.get(CacheService)

# Cleanup (or use context manager)
container.close()

# Better: use context manager
with svcs.Container(registry) as container:
    db = container.get(DatabaseService)
    # Automatically cleaned up
```

## Best Practices

✅ **DO**:
- Use `@dataclass(frozen=True)` for immutability
- Use `Inject[T]` to mark dependencies explicitly
- Use `auto()` to wrap types with dependencies
- Use `@injectable` decorator for auto-discovery in large apps
- Keep services stateless (no business logic)
- Use fakes in tests, not mocks
- Use protocols for interface-based dependency injection
- Create one registry per application
- Create one container per request/operation
- Close containers when done (or use context manager)

❌ **DON'T**:
- Make services that contain business logic
- Store mutable business state in services
- Mark all parameters with `Inject` - only use for actual dependencies
- Share containers across requests
- Forget to close containers with cleanup callbacks

## svcs-di Advanced Features

### KeywordInjector (Three-Tier Precedence)

Override dependencies at construction time for testing:

```python
import svcs
from svcs_di import auto
from svcs_di.injectors import KeywordInjector

# Register KeywordInjector
registry = svcs.Registry()
registry.register_factory(
    KeywordInjector,
    lambda c: KeywordInjector(container=c)
)
registry.register_factory(CacheService, auto(CacheService))

# Can now override at get() time
container = svcs.Container(registry)
service = container.get(CacheService, db=test_db, ttl=60)
```

**Three-tier precedence**:
1. kwargs overrides (highest priority)
2. container services
3. default values (lowest priority)

### @injectable Decorator Options

The `@injectable` decorator supports resource-based and location-based registration:

```python
from pathlib import PurePath
from svcs_di.injectors.decorators import injectable

# Simple registration (default)
@injectable
@dataclass
class DefaultService:
    pass

# Resource-based (for specific contexts)
@injectable(resource=EmployeeContext)
@dataclass
class EmployeeService:
    pass

# Location-based (for URL paths)
@injectable(location=PurePath("/admin"))
@dataclass
class AdminService:
    pass

# Multiple implementations via for_ parameter
@injectable(for_=Greeting)
@dataclass
class DefaultGreeting:
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"
```

### For More Advanced Patterns

See the `svcs-di` project for:
- **HopscotchInjector**: Multiple implementations with resource/location-based resolution
- **ServiceLocator**: Register multiple implementations of the same service type
- **scan() function**: Auto-discovery via package scanning

## Quick Reference

```python
import svcs
from svcs_di import Inject, auto
from dataclasses import dataclass

# Define service with dependencies
@dataclass
class MyService:
    dependency: Inject[OtherService]
    config: str = "default"

# Manual registration
registry = svcs.Registry()
registry.register_factory(OtherService, OtherService)
registry.register_factory(MyService, auto(MyService))

# Or use @injectable decorator
from svcs_di.injectors.decorators import injectable
from svcs_di.injectors.locator import scan

@injectable
@dataclass
class MyService:
    dependency: Inject[OtherService]

registry = svcs.Registry()
scan(registry)  # Auto-registers @injectable classes

# Use services
container = svcs.Container(registry)
service = container.get(MyService)

# Test with fakes
fake_dep = OtherService()
test_registry = svcs.Registry()
test_registry.register_value(OtherService, fake_dep)
test_registry.register_factory(MyService, auto(MyService))
test_container = svcs.Container(test_registry)
test_service = test_container.get(MyService)
assert test_service.dependency is fake_dep
```

## Further Reading

- [svcs documentation](https://svcs.hynek.me/)
- [svcs-di project](../svcs-di/) - Automatic dependency injection for svcs
- [Architecture Patterns with Python](https://www.cosmicpython.com/) - Service Layer pattern
- svcs glossary for: Service Layer, Dependency Injection, Service Locator, Hexagonal Architecture
