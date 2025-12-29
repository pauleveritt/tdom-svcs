"""Tests for middleware integration with component lifecycle hooks.

This test module verifies that middleware executes at the correct points in the
component lifecycle (pre-resolution, post-resolution, rendering) and that both
global and per-component middleware work correctly with proper priority ordering.
"""

import pytest
from dataclasses import dataclass
from typing import Any, Callable
from collections.abc import Mapping

from tdom_svcs.services.middleware import (
    Context,
    Middleware,
    MiddlewareManager,
    component,
    get_component_middleware,
)


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
        comp_name = component.__name__ if hasattr(component, "__name__") else str(component)
        self.execution_log.append(f"{self.name}({comp_name})")
        # Add marker to props to track middleware execution
        props[f"_middleware_{self.name}"] = True
        return props


def test_middleware_execution_order_with_priorities() -> None:
    """Test that middleware executes in priority order (lower numbers first)."""
    execution_log: list[str] = []

    # Create middleware with different priorities
    mw1 = MockMiddleware(name="mw1", priority=-10, execution_log=execution_log)
    mw2 = MockMiddleware(name="mw2", priority=0, execution_log=execution_log)
    mw3 = MockMiddleware(name="mw3", priority=10, execution_log=execution_log)

    # Register middleware
    manager = MiddlewareManager()
    manager.register_middleware(mw3)  # Register out of order
    manager.register_middleware(mw1)
    manager.register_middleware(mw2)

    # Execute middleware
    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    props = {"value": "test"}
    context: dict[str, Any] = {}

    result = manager.execute(TestComponent, props, context)

    # Verify execution order (lower priority first)
    assert execution_log == ["mw1(TestComponent)", "mw2(TestComponent)", "mw3(TestComponent)"]
    assert result is not None
    assert result["_middleware_mw1"] is True
    assert result["_middleware_mw2"] is True
    assert result["_middleware_mw3"] is True


def test_global_middleware_executes_before_per_component_middleware() -> None:
    """Test that global middleware executes before per-component middleware."""
    execution_log: list[str] = []

    # Create global middleware
    global_mw = MockMiddleware(name="global", priority=0, execution_log=execution_log)

    # Create per-component middleware
    component_mw = MockMiddleware(name="component", priority=0, execution_log=execution_log)

    # Register global middleware
    manager = MiddlewareManager()
    manager.register_middleware(global_mw)

    @component(middleware={"pre_resolution": [component_mw]})
    @dataclass
    class TestComponent:
        """Test component with per-component middleware."""

        value: str = "test"

    # Execute global middleware
    props = {"value": "test"}
    context: dict[str, Any] = {}
    props_after_global = manager.execute(TestComponent, props, context)

    # Execute per-component middleware
    component_middleware = get_component_middleware(TestComponent)
    pre_resolution_middleware = component_middleware.get("pre_resolution", [])

    assert props_after_global is not None
    for mw in sorted(pre_resolution_middleware, key=lambda m: m.priority):
        props_after_global = mw(TestComponent, props_after_global, context)

    # Verify execution order: global then component
    assert execution_log == ["global(TestComponent)", "component(TestComponent)"]
    assert props_after_global is not None
    assert props_after_global["_middleware_global"] is True
    assert props_after_global["_middleware_component"] is True


def test_middleware_works_with_class_components() -> None:
    """Test that middleware works correctly with class components."""
    execution_log: list[str] = []

    mw = MockMiddleware(name="test", priority=0, execution_log=execution_log)
    manager = MiddlewareManager()
    manager.register_middleware(mw)

    @dataclass
    class ClassComponent:
        """Class-based component."""

        label: str = "Button"

    props = {"label": "Click"}
    context: dict[str, Any] = {}

    result = manager.execute(ClassComponent, props, context)

    assert execution_log == ["test(ClassComponent)"]
    assert result is not None
    assert result["_middleware_test"] is True
    # Verify component is detected as class
    assert isinstance(ClassComponent, type)


def test_middleware_works_with_function_components() -> None:
    """Test that middleware works correctly with function components."""
    execution_log: list[str] = []

    mw = MockMiddleware(name="test", priority=0, execution_log=execution_log)
    manager = MiddlewareManager()
    manager.register_middleware(mw)

    def function_component(text: str = "Hello") -> str:
        """Function-based component."""
        return f"<div>{text}</div>"

    props = {"text": "World"}
    context: dict[str, Any] = {}

    result = manager.execute(function_component, props, context)

    assert execution_log == ["test(function_component)"]
    assert result is not None
    assert result["_middleware_test"] is True
    # Verify component is detected as function
    assert not isinstance(function_component, type)


def test_per_component_middleware_respects_priority_ordering() -> None:
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

    # Execute per-component middleware in priority order
    component_middleware = get_component_middleware(TestComponent)
    pre_resolution_middleware = component_middleware.get("pre_resolution", [])

    props = {"value": "test"}
    context: dict[str, Any] = {}

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


def test_middleware_halt_stops_execution() -> None:
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
    mw_after_halt = MockMiddleware(name="after_halt", priority=10, execution_log=execution_log)

    manager = MiddlewareManager()
    manager.register_middleware(HaltingMiddleware())
    manager.register_middleware(mw_after_halt)

    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    props = {"value": "test"}
    context: dict[str, Any] = {}

    result = manager.execute(TestComponent, props, context)

    # Verify halting middleware executed but after_halt did not
    assert execution_log == ["halting_middleware"]
    assert result is None  # Execution halted


def test_middleware_integration_with_multiple_lifecycle_phases() -> None:
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

    # Verify middleware is stored for both phases
    component_middleware = get_component_middleware(TestComponent)
    assert "pre_resolution" in component_middleware
    assert "post_resolution" in component_middleware
    assert len(component_middleware["pre_resolution"]) == 1
    assert len(component_middleware["post_resolution"]) == 1

    # Execute pre-resolution middleware
    props = {"value": "test"}
    context: dict[str, Any] = {}

    for mw in component_middleware["pre_resolution"]:
        props = mw(TestComponent, props, context)

    assert pre_log == ["pre(TestComponent)"]

    # Execute post-resolution middleware
    for mw in component_middleware["post_resolution"]:
        props = mw(TestComponent, props, context)

    assert post_log == ["post(TestComponent)"]
