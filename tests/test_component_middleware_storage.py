"""Tests verifying component middleware is stored only on the class, not in registry."""

from dataclasses import dataclass

from svcs_di.injectors import HopscotchRegistry, HopscotchContainer

from tdom_svcs import component, middleware, scan, execute_component_middleware
from tdom_svcs.services.middleware.decorators import COMPONENT_MIDDLEWARE_ATTR


@middleware
@dataclass
class StorageTestMiddleware:
    """Test middleware for storage verification.

    Note: This middleware IS decorated with @middleware so it can be resolved
    from the DI container. The key insight is that the middleware TYPE needs to
    be registered, but the component's MIDDLEWARE CONFIG (MiddlewareMap) doesn't
    need separate registry storage - it's read directly from the class attribute.
    """

    priority: int = 0

    def __call__(self, component, props, context):
        props["middleware_executed"] = True
        return props


def test_component_middleware_stored_only_on_class():
    """Verify middleware config is stored only on class, not in registry metadata."""

    @component(middleware={"pre_resolution": [StorageTestMiddleware]})
    @dataclass
    class TestComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    scan(registry, locals_dict=locals())

    # Should be on the class
    class_config = getattr(TestComponent, COMPONENT_MIDDLEWARE_ATTR, None)
    assert class_config is not None
    assert "pre_resolution" in class_config
    assert StorageTestMiddleware in class_config["pre_resolution"]

    # Should NOT be in registry metadata (no longer stored there)
    # The old COMPONENT_MW_REGISTRY_KEY has been removed
    assert not hasattr(registry, "_component_middleware")


def test_middleware_execution_reads_from_class():
    """Verify execution reads middleware config directly from class attribute."""
    from tdom_svcs import register_middleware

    @component(middleware={"pre_resolution": [StorageTestMiddleware]})
    @dataclass
    class TestComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    # Explicitly register the middleware type so it can be resolved from container
    register_middleware(registry, StorageTestMiddleware)
    scan(registry, locals_dict=locals())

    # Execute middleware
    with HopscotchContainer(registry) as container:
        props = {}
        result = execute_component_middleware(
            TestComponent, props, container, "pre_resolution"
        )

    # Should have executed successfully by reading from class
    assert result is not None
    assert result["middleware_executed"] is True


def test_runtime_modification_of_class_attribute():
    """Verify we can modify middleware config at runtime via class attribute."""
    from tdom_svcs import register_middleware

    @component
    @dataclass
    class DynamicComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    # Register middleware type for DI resolution
    register_middleware(registry, StorageTestMiddleware)
    scan(registry, locals_dict=locals())

    # Initially no middleware
    with HopscotchContainer(registry) as container:
        props = {}
        result = execute_component_middleware(
            DynamicComponent, props, container, "pre_resolution"
        )
    assert "middleware_executed" not in result

    # Add middleware at runtime by modifying class attribute
    setattr(
        DynamicComponent,
        COMPONENT_MIDDLEWARE_ATTR,
        {"pre_resolution": [StorageTestMiddleware]},
    )

    # Now middleware should execute
    with HopscotchContainer(registry) as container:
        props = {}
        result = execute_component_middleware(
            DynamicComponent, props, container, "pre_resolution"
        )
    assert result["middleware_executed"] is True


def test_no_registry_pollution():
    """Verify component middleware doesn't pollute registry metadata."""

    @component(middleware={"pre_resolution": [StorageTestMiddleware]})
    @dataclass
    class CleanComponent:
        value: str = "test"

    registry = HopscotchRegistry()

    # Check registry metadata before scan
    initial_metadata_keys = set(registry._metadata.keys()) if hasattr(registry, '_metadata') else set()

    scan(registry, locals_dict=locals())

    # Check registry metadata after scan
    final_metadata_keys = set(registry._metadata.keys()) if hasattr(registry, '_metadata') else set()

    # Component middleware should not add any metadata keys
    # (The component itself gets registered, but not its middleware config)
    new_keys = final_metadata_keys - initial_metadata_keys

    # Should not have added component middleware key
    assert not any("component_middleware" in str(key).lower() for key in new_keys)


def test_imperative_registration_uses_class_attribute():
    """Verify imperative registration also uses class attribute storage."""
    from tdom_svcs import register_middleware
    from tdom_svcs.services.middleware import register_component

    @dataclass
    class ImperativeComponent:
        value: str = "test"

    registry = HopscotchRegistry()
    # Register middleware type for DI resolution
    register_middleware(registry, StorageTestMiddleware)
    register_component(
        registry,
        ImperativeComponent,
        middleware={"pre_resolution": [StorageTestMiddleware]},
    )

    # Should be stored on class
    class_config = getattr(ImperativeComponent, COMPONENT_MIDDLEWARE_ATTR, None)
    assert class_config is not None
    assert "pre_resolution" in class_config

    # Should execute
    scan(registry, locals_dict=locals())
    with HopscotchContainer(registry) as container:
        props = {}
        result = execute_component_middleware(
            ImperativeComponent, props, container, "pre_resolution"
        )
    assert result["middleware_executed"] is True
