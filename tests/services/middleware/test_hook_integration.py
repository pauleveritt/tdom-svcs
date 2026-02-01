"""Tests for middleware integration with component lifecycle hooks.

This test module verifies that middleware executes at the correct points in the
component lifecycle (pre-resolution, post-resolution, rendering) and that both
global and per-component middleware work correctly with proper priority ordering.
"""

from dataclasses import dataclass
from typing import Any, Callable, cast

from tdom_svcs import (
    component,
    execute_middleware,
    get_component_middleware,
    register_middleware,
    scan,
)
from tdom_svcs.services.middleware import Context


@dataclass
class MockMiddleware:
    """Mock middleware for testing execution order."""

    name: str
    priority: int
    execution_log: list[str]

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Record execution and modify props."""
        comp_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.execution_log.append(f"{self.name}({comp_name})")
        # Add marker to props to track middleware execution
        props[f"_middleware_{self.name}"] = True
        return props


def test_middleware_execution_order_with_priorities(registry, container) -> None:
    """Test that middleware executes in priority order (lower numbers first)."""
    execution_log: list[str] = []

    # Create middleware with different priorities
    mw1 = MockMiddleware(name="mw1", priority=-10, execution_log=execution_log)
    mw2 = MockMiddleware(name="mw2", priority=0, execution_log=execution_log)
    mw3 = MockMiddleware(name="mw3", priority=10, execution_log=execution_log)

    # Use a wrapper class for each to register with DI
    @dataclass
    class Mw1Wrapper:
        priority: int = -10

        def __call__(self, comp, props, ctx):
            return mw1(comp, props, ctx)

    @dataclass
    class Mw2Wrapper:
        priority: int = 0

        def __call__(self, comp, props, ctx):
            return mw2(comp, props, ctx)

    @dataclass
    class Mw3Wrapper:
        priority: int = 10

        def __call__(self, comp, props, ctx):
            return mw3(comp, props, ctx)

    # Register middleware as values
    registry.register_value(Mw1Wrapper, Mw1Wrapper())
    registry.register_value(Mw2Wrapper, Mw2Wrapper())
    registry.register_value(Mw3Wrapper, Mw3Wrapper())

    # Register middleware (out of order)
    register_middleware(registry, Mw3Wrapper)
    register_middleware(registry, Mw1Wrapper)
    register_middleware(registry, Mw2Wrapper)

    # Execute middleware
    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    props = {"value": "test"}

    result = execute_middleware(TestComponent, props, container)

    # Verify execution order (lower priority first)
    assert execution_log == [
        "mw1(TestComponent)",
        "mw2(TestComponent)",
        "mw3(TestComponent)",
    ]
    assert result is not None
    assert result["_middleware_mw1"] is True
    assert result["_middleware_mw2"] is True
    assert result["_middleware_mw3"] is True


def test_global_middleware_executes_before_per_component_middleware(
    registry, container
) -> None:
    """Test that global middleware executes before per-component middleware."""
    execution_log: list[str] = []

    # Create global middleware
    global_mw = MockMiddleware(name="global", priority=0, execution_log=execution_log)

    # Create per-component middleware
    component_mw = MockMiddleware(
        name="component", priority=0, execution_log=execution_log
    )

    @dataclass
    class GlobalMwWrapper:
        priority: int = 0

        def __call__(self, comp, props, ctx):
            return global_mw(comp, props, ctx)

    registry.register_value(GlobalMwWrapper, GlobalMwWrapper())
    register_middleware(registry, GlobalMwWrapper)

    @component(middleware={"pre_resolution": [component_mw]})
    @dataclass
    class TestComponent:
        """Test component with per-component middleware."""

        value: str = "test"

    # Scan to register component middleware
    scan(registry, locals_dict={"TestComponent": TestComponent})

    # Execute global middleware
    props = {"value": "test"}
    props_after_global = execute_middleware(TestComponent, props, container)

    # Execute per-component middleware
    component_middleware = get_component_middleware(registry, TestComponent)
    pre_resolution_middleware = component_middleware.get("pre_resolution", [])

    assert props_after_global is not None
    for mw in sorted(pre_resolution_middleware, key=lambda m: m.priority):
        result = mw(TestComponent, props_after_global, container)
        assert result is not None
        # In this test, all middleware is synchronous
        props_after_global = cast(dict[str, Any], result)

    # Verify execution order: global then component
    assert execution_log == ["global(TestComponent)", "component(TestComponent)"]
    assert props_after_global["_middleware_global"] is True
    assert props_after_global["_middleware_component"] is True


def test_middleware_works_with_class_components(registry, container) -> None:
    """Test that middleware works correctly with class components."""
    execution_log: list[str] = []

    mw = MockMiddleware(name="test", priority=0, execution_log=execution_log)

    @dataclass
    class MwWrapper:
        priority: int = 0

        def __call__(self, comp, props, ctx):
            return mw(comp, props, ctx)

    registry.register_value(MwWrapper, MwWrapper())
    register_middleware(registry, MwWrapper)

    @dataclass
    class ClassComponent:
        """Class-based component."""

        label: str = "Button"

    props = {"label": "Click"}

    result = execute_middleware(ClassComponent, props, container)

    assert execution_log == ["test(ClassComponent)"]
    assert result is not None
    assert result["_middleware_test"] is True
    # Verify component is detected as class
    assert isinstance(ClassComponent, type)


def test_middleware_works_with_function_components(registry, container) -> None:
    """Test that middleware works correctly with function components."""
    execution_log: list[str] = []

    mw = MockMiddleware(name="test", priority=0, execution_log=execution_log)

    @dataclass
    class MwWrapper:
        priority: int = 0

        def __call__(self, comp, props, ctx):
            return mw(comp, props, ctx)

    registry.register_value(MwWrapper, MwWrapper())
    register_middleware(registry, MwWrapper)

    def function_component(text: str = "Hello") -> str:
        """Function-based component."""
        return f"<div>{text}</div>"

    props = {"text": "World"}

    result = execute_middleware(function_component, props, container)

    assert execution_log == ["test(function_component)"]
    assert result is not None
    assert result["_middleware_test"] is True
    # Verify component is detected as function
    assert not isinstance(function_component, type)


def test_per_component_middleware_respects_priority_ordering(registry) -> None:
    """Test that per-component middleware respects priority ordering."""
    execution_log: list[str] = []

    # Create per-component middleware with different priorities
    mw1 = MockMiddleware(name="comp_mw1", priority=-10, execution_log=execution_log)
    mw2 = MockMiddleware(name="comp_mw2", priority=0, execution_log=execution_log)
    mw3 = MockMiddleware(name="comp_mw3", priority=10, execution_log=execution_log)

    @component(middleware={"pre_resolution": [mw3, mw1, mw2]})  # Register out of order
    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    # Scan to register component middleware
    scan(registry, locals_dict={"TestComponent": TestComponent})

    # Execute per-component middleware in priority order
    component_middleware = get_component_middleware(registry, TestComponent)
    pre_resolution_middleware = component_middleware.get("pre_resolution", [])

    props = {"value": "test"}
    context: Context = cast(Context, {})

    current_props = props
    for mw in sorted(pre_resolution_middleware, key=lambda m: m.priority):
        current_props = mw(TestComponent, current_props, context)

    # Verify execution order (lower priority first)
    assert execution_log == [
        "comp_mw1(TestComponent)",
        "comp_mw2(TestComponent)",
        "comp_mw3(TestComponent)",
    ]
    assert current_props is not None


def test_middleware_halt_stops_execution(registry, container) -> None:
    """Test that returning None from middleware halts execution."""
    execution_log: list[str] = []

    # Create middleware that halts
    @dataclass
    class HaltingMiddleware:
        priority: int = 0

        def __call__(
            self,
            component: type | Callable[..., Any],
            props: dict[str, Any],
            context: Context,
        ) -> dict[str, Any] | None:
            execution_log.append("halting_middleware")
            return None  # Halt execution

    # Create middleware that should not execute
    mw_after_halt = MockMiddleware(
        name="after_halt", priority=10, execution_log=execution_log
    )

    @dataclass
    class MwAfterHaltWrapper:
        priority: int = 10

        def __call__(self, comp, props, ctx):
            return mw_after_halt(comp, props, ctx)

    registry.register_value(HaltingMiddleware, HaltingMiddleware())
    registry.register_value(MwAfterHaltWrapper, MwAfterHaltWrapper())
    register_middleware(registry, HaltingMiddleware)
    register_middleware(registry, MwAfterHaltWrapper)

    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    props = {"value": "test"}

    result = execute_middleware(TestComponent, props, container)

    # Verify halting middleware executed but after_halt did not
    assert execution_log == ["halting_middleware"]
    assert result is None  # Execution halted


def test_middleware_integration_with_multiple_lifecycle_phases(registry) -> None:
    """Test middleware can be registered for multiple lifecycle phases."""
    pre_log: list[str] = []
    post_log: list[str] = []

    pre_mw = MockMiddleware(name="pre", priority=0, execution_log=pre_log)
    post_mw = MockMiddleware(name="post", priority=0, execution_log=post_log)

    @component(
        middleware={
            "pre_resolution": [pre_mw],
            "post_resolution": [post_mw],
        }
    )
    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    # Scan to register component middleware
    scan(registry, locals_dict={"TestComponent": TestComponent})

    # Verify middleware is stored for both phases
    component_middleware = get_component_middleware(registry, TestComponent)
    assert "pre_resolution" in component_middleware
    assert "post_resolution" in component_middleware
    assert len(component_middleware["pre_resolution"]) == 1
    assert len(component_middleware["post_resolution"]) == 1

    # Execute pre-resolution middleware
    props = {"value": "test"}
    context: Context = cast(Context, {})

    for mw in component_middleware["pre_resolution"]:
        result = mw(TestComponent, props, context)
        assert result is not None
        props = cast(dict[str, Any], result)

    assert pre_log == ["pre(TestComponent)"]

    # Execute post-resolution middleware
    for mw in component_middleware["post_resolution"]:
        result = mw(TestComponent, props, context)
        assert result is not None
        props = cast(dict[str, Any], result)

    assert post_log == ["post(TestComponent)"]
