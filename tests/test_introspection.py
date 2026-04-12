"""Tests for registry introspection helpers."""

from dataclasses import dataclass
from pathlib import PurePath

from markupsafe import Markup
from svcs_hopscotch.injectors import HopscotchRegistry

from tdom_svcs import (
    ComponentInfo,
    MiddlewareInfo,
    list_components,
    list_middlewares,
    middleware,
    scan,
)


# Test components
@dataclass
class Database:
    """Simple database service."""

    host: str = "localhost"


@dataclass
class PostgresDB(Database):
    """PostgreSQL implementation."""

    pass


@dataclass
class MySQLDB(Database):
    """MySQL implementation."""

    pass


@dataclass
class Greeting:
    """Greeting component."""

    def __call__(self) -> str | Markup:
        return Markup("<h1>Hello</h1>")


# Test context types
class EmployeeContext:
    """Employee resource type."""

    pass


class CustomerContext:
    """Customer resource type."""

    pass


# Test middleware
@dataclass
class LoggingMiddleware:
    """Logging middleware for testing."""

    priority: int = -10

    def __call__(self, component, props, context):
        return props


@dataclass
class AuthMiddleware:
    """Auth middleware for testing."""

    priority: int = -20

    def __call__(self, component, props, context):
        return props


def test_list_components_empty_registry():
    """Empty registry returns empty dict."""
    registry = HopscotchRegistry()
    result = list_components(registry)

    assert result == {}
    assert isinstance(result, dict)


def test_list_components_single_registration():
    """Single registration returns correct ComponentInfo."""
    registry = HopscotchRegistry()

    class SimpleService:
        pass

    registry.register_implementation(SimpleService, SimpleService)

    result = list_components(registry)

    assert SimpleService in result
    info = result[SimpleService]
    assert isinstance(info, ComponentInfo)
    assert info.service_type is SimpleService
    assert len(info.variations) == 1
    assert info.variations[0].implementation is SimpleService
    assert info.variations[0].resource is None
    assert info.variations[0].location is None


def test_list_components_multiple_variations_same_type():
    """Multiple variations for same service type are grouped together."""
    registry = HopscotchRegistry()

    # Register base implementation
    registry.register_implementation(Database, PostgresDB)
    # Register resource-specific implementation
    registry.register_implementation(Database, MySQLDB, resource=EmployeeContext)

    result = list_components(registry)

    assert Database in result
    info = result[Database]
    assert len(info.variations) == 2

    # Check that both implementations are present
    implementations = {v.implementation for v in info.variations}
    assert PostgresDB in implementations
    assert MySQLDB in implementations

    # Check resource association
    mysql_variation = next(v for v in info.variations if v.implementation is MySQLDB)
    assert mysql_variation.resource is EmployeeContext


def test_list_components_location_based_registration():
    """Location-based registrations are captured correctly."""
    registry = HopscotchRegistry()

    # Register location-specific implementation
    admin_location = PurePath("/admin")
    registry.register_implementation(Greeting, Greeting, location=admin_location)

    result = list_components(registry)

    assert Greeting in result
    info = result[Greeting]
    assert len(info.variations) == 1
    assert info.variations[0].location == admin_location


def test_list_components_combined_resource_and_location():
    """Combined resource + location registrations work correctly."""
    registry = HopscotchRegistry()

    admin_location = PurePath("/admin")
    registry.register_implementation(
        Database, PostgresDB, resource=EmployeeContext, location=admin_location
    )

    result = list_components(registry)

    assert Database in result
    info = result[Database]
    assert len(info.variations) == 1
    variation = info.variations[0]
    assert variation.implementation is PostgresDB
    assert variation.resource is EmployeeContext
    assert variation.location == admin_location


def test_list_components_multiple_service_types():
    """Multiple different service types are all returned."""
    registry = HopscotchRegistry()

    class ServiceA:
        pass

    class ServiceB:
        pass

    class ServiceC:
        pass

    registry.register_implementation(ServiceA, ServiceA)
    registry.register_implementation(ServiceB, ServiceB)
    registry.register_implementation(ServiceC, ServiceC)

    result = list_components(registry)

    assert len(result) == 3
    assert ServiceA in result
    assert ServiceB in result
    assert ServiceC in result


def test_list_middlewares_empty_registry():
    """Empty registry returns empty tuple."""
    registry = HopscotchRegistry()
    result = list_middlewares(registry)

    assert result == ()
    assert isinstance(result, tuple)


def test_list_middlewares_single_middleware():
    """Single middleware registration returns correct MiddlewareInfo."""
    registry = HopscotchRegistry()

    @middleware
    @dataclass
    class SimpleMiddleware:
        priority: int = 5

        def __call__(self, component, props, context):
            return props

    scan(registry, locals_dict=locals())

    result = list_middlewares(registry)

    assert len(result) == 1
    info = result[0]
    assert isinstance(info, MiddlewareInfo)
    assert info.middleware_type is SimpleMiddleware
    assert info.priority == 5


def test_list_middlewares_multiple_middlewares():
    """Multiple middleware registrations are all returned."""
    registry = HopscotchRegistry()

    @middleware
    @dataclass
    class MiddlewareA:
        priority: int = -10

        def __call__(self, component, props, context):
            return props

    @middleware
    @dataclass
    class MiddlewareB:
        priority: int = -20

        def __call__(self, component, props, context):
            return props

    scan(registry, locals_dict=locals())

    result = list_middlewares(registry)

    assert len(result) == 2
    middleware_types = {info.middleware_type for info in result}
    assert MiddlewareA in middleware_types
    assert MiddlewareB in middleware_types


def test_list_middlewares_extracts_priority():
    """Middleware priority is correctly extracted from dataclass field."""
    registry = HopscotchRegistry()

    @middleware
    @dataclass
    class LogMiddleware:
        priority: int = -15

        def __call__(self, component, props, context):
            return props

    scan(registry, locals_dict=locals())

    result = list_middlewares(registry)

    assert len(result) == 1
    assert result[0].priority == -15


def test_list_middlewares_no_priority_field():
    """Middleware without priority field has None priority."""
    registry = HopscotchRegistry()

    @middleware
    class NoPriorityMiddleware:
        def __call__(self, component, props, context):
            return props

    scan(registry, locals_dict=locals())

    result = list_middlewares(registry)

    assert len(result) == 1
    assert result[0].middleware_type is NoPriorityMiddleware
    assert result[0].priority is None


def test_introspection_with_real_registry():
    """Integration test with realistic registry setup."""
    registry = HopscotchRegistry()

    # Register components
    registry.register_implementation(Database, PostgresDB)
    registry.register_implementation(Database, MySQLDB, resource=EmployeeContext)

    class Cache:
        pass

    registry.register_implementation(Cache, Cache)

    # Register middleware
    @middleware
    @dataclass
    class AuthMw:
        priority: int = -100

        def __call__(self, component, props, context):
            return props

    @middleware
    @dataclass
    class LogMw:
        priority: int = -50

        def __call__(self, component, props, context):
            return props

    scan(registry, locals_dict=locals())

    # Inspect components
    components = list_components(registry)
    assert len(components) == 2  # Database and Cache
    assert Database in components
    assert Cache in components

    db_info = components[Database]
    assert len(db_info.variations) == 2

    # Inspect middleware
    middlewares = list_middlewares(registry)
    assert len(middlewares) == 2

    priorities = {info.priority for info in middlewares}
    assert priorities == {-100, -50}
