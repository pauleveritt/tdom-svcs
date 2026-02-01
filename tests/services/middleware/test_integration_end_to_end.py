"""Integration tests for complete middleware system workflows.

This test module fills critical gaps in middleware testing by focusing on
end-to-end integration scenarios across the entire middleware system.
"""

import asyncio
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, cast

import pytest

from tdom_svcs import (
    component,
    execute_middleware,
    execute_middleware_async,
    get_component_middleware,
    register_middleware,
    scan,
)
from tdom_svcs.services.middleware import Context


# Test fixtures


@dataclass
class ExecutionTracker:
    """Shared tracker for recording middleware execution order."""

    executions: list[str] = field(default_factory=list)

    def record(self, event: str) -> None:
        """Record an execution event."""
        self.executions.append(event)


@dataclass
class LoggingMiddleware:
    """Global logging middleware for integration testing."""

    priority: int
    tracker: ExecutionTracker

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Log component execution."""
        comp_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.tracker.record(f"global_logging({comp_name})")
        props["logged"] = True
        return props


@dataclass
class ValidationMiddleware:
    """Global validation middleware."""

    priority: int
    tracker: ExecutionTracker

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Validate props."""
        comp_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.tracker.record(f"global_validation({comp_name})")
        # Halt if invalid prop
        if props.get("invalid"):
            return None
        props["validated"] = True
        return props


@dataclass
class TransformationMiddleware:
    """Per-component transformation middleware."""

    priority: int
    tracker: ExecutionTracker
    transform_key: str

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Transform props."""
        comp_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.tracker.record(f"component_transform({comp_name})")
        props[self.transform_key] = f"transformed_{props.get(self.transform_key, '')}"
        return props


@dataclass
class AsyncMiddleware:
    """Async middleware for testing mixed chains."""

    priority: int
    tracker: ExecutionTracker

    async def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Async middleware execution."""
        comp_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        # Simulate async work
        await asyncio.sleep(0.001)
        self.tracker.record(f"async_middleware({comp_name})")
        props["async_processed"] = True
        return props


@dataclass
class StatefulAssetCollector:
    """Stateful middleware stored in context."""

    assets: list[str] = field(default_factory=list)

    def collect(self, asset: str) -> None:
        """Collect an asset."""
        self.assets.append(asset)


@dataclass
class AssetCollectionMiddleware:
    """Middleware that uses stateful service from context."""

    priority: int
    tracker: ExecutionTracker
    asset_collector: StatefulAssetCollector

    def __call__(
        self,
        component: type | Callable[..., Any],
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Collect assets from context."""
        comp_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        self.tracker.record(f"asset_collection({comp_name})")
        self.asset_collector.collect(comp_name)
        return props


# Integration tests


def test_end_to_end_workflow_with_setup_and_execution(registry, container) -> None:
    """Test complete workflow: register -> execute -> integrate.

    This test covers the critical integration path from initial setup through
    full middleware execution with both global and per-component middleware.
    """
    # Step 1: Setup tracker and create middleware instances
    tracker = ExecutionTracker()
    asset_collector = StatefulAssetCollector()

    # Create middleware instances with specific state
    logging_mw = LoggingMiddleware(priority=-10, tracker=tracker)
    validation_mw = ValidationMiddleware(priority=0, tracker=tracker)
    asset_mw = AssetCollectionMiddleware(priority=10, tracker=tracker, asset_collector=asset_collector)

    # Step 2: Register middleware as values in registry
    @dataclass
    class LoggingMwType:
        priority: int = -10

        def __call__(self, comp, props, ctx):
            return logging_mw(comp, props, ctx)

    @dataclass
    class ValidationMwType:
        priority: int = 0

        def __call__(self, comp, props, ctx):
            return validation_mw(comp, props, ctx)

    @dataclass
    class AssetMwType:
        priority: int = 10

        def __call__(self, comp, props, ctx):
            return asset_mw(comp, props, ctx)

    registry.register_value(LoggingMwType, LoggingMwType())
    registry.register_value(ValidationMwType, ValidationMwType())
    registry.register_value(AssetMwType, AssetMwType())

    register_middleware(registry, LoggingMwType)
    register_middleware(registry, ValidationMwType)
    register_middleware(registry, AssetMwType)

    # Step 3: Define components with per-component middleware
    transform_mw = TransformationMiddleware(
        priority=5, tracker=tracker, transform_key="label"
    )

    @component(middleware={"pre_resolution": [transform_mw]})
    @dataclass
    class Button:
        """Button component with transformation middleware."""

        label: str = "Click"

    def heading(text: str = "Title") -> str:
        """Heading function component."""
        return f"<h1>{text}</h1>"

    # Scan to register component middleware
    scan(registry, locals_dict={"Button": Button})

    # Step 4: Execute middleware for class component
    props_button = {"label": "Submit"}
    result_button = execute_middleware(Button, props_button, container)

    # Execute per-component middleware
    assert result_button is not None
    component_mw = get_component_middleware(registry, Button)
    for mw in sorted(component_mw.get("pre_resolution", []), key=lambda m: m.priority):
        result = mw(Button, result_button, container)
        assert result is not None
        result_button = cast(dict[str, Any], result)

    # Step 5: Execute middleware for function component
    props_heading = {"text": "Welcome"}
    result_heading = execute_middleware(heading, props_heading, container)

    # Verify complete execution order
    expected_order = [
        "global_logging(Button)",
        "global_validation(Button)",
        "asset_collection(Button)",
        "component_transform(Button)",
        "global_logging(heading)",
        "global_validation(heading)",
        "asset_collection(heading)",
    ]
    assert tracker.executions == expected_order

    # Verify all middleware executed correctly
    assert result_button is not None
    assert result_button["logged"] is True
    assert result_button["validated"] is True
    assert result_button["label"] == "transformed_Submit"

    assert result_heading is not None
    assert result_heading["logged"] is True
    assert result_heading["validated"] is True

    # Verify stateful middleware worked
    assert asset_collector.assets == ["Button", "heading"]


@pytest.mark.anyio
async def test_mixed_sync_async_middleware_chain(registry, container) -> None:
    """Test comprehensive mixed sync/async middleware execution.

    Verifies that sync and async middleware can be mixed in any order
    and execute correctly maintaining priority ordering.
    """
    tracker = ExecutionTracker()

    logging_mw = LoggingMiddleware(priority=-10, tracker=tracker)
    async_mw = AsyncMiddleware(priority=5, tracker=tracker)
    validation_mw = ValidationMiddleware(priority=10, tracker=tracker)

    @dataclass
    class LoggingMwType:
        priority: int = -10

        def __call__(self, comp, props, ctx):
            return logging_mw(comp, props, ctx)

    @dataclass
    class AsyncMwType:
        priority: int = 5

        async def __call__(self, comp, props, ctx):
            return await async_mw(comp, props, ctx)

    @dataclass
    class ValidationMwType:
        priority: int = 10

        def __call__(self, comp, props, ctx):
            return validation_mw(comp, props, ctx)

    registry.register_value(LoggingMwType, LoggingMwType())
    registry.register_value(AsyncMwType, AsyncMwType())
    registry.register_value(ValidationMwType, ValidationMwType())

    register_middleware(registry, LoggingMwType)
    register_middleware(registry, AsyncMwType)
    register_middleware(registry, ValidationMwType)

    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    props = {"value": "test"}

    # Execute async chain
    result = await execute_middleware_async(TestComponent, props, container)

    # Verify order: logging (-10), async (5), validation (10)
    expected_order = [
        "global_logging(TestComponent)",
        "async_middleware(TestComponent)",
        "global_validation(TestComponent)",
    ]
    assert tracker.executions == expected_order

    assert result is not None
    assert result["logged"] is True
    assert result["async_processed"] is True
    assert result["validated"] is True


def test_error_propagation_from_middleware(registry, container) -> None:
    """Test that middleware exceptions propagate correctly.

    Verifies that exceptions raised by middleware are not swallowed
    and propagate to the caller for proper error handling.
    """

    @dataclass
    class ErrorMiddleware:
        """Middleware that raises an exception."""

        priority: int = 0

        def __call__(
            self,
            component: type | Callable[..., Any],
            props: dict[str, Any],
            context: Context,
        ) -> dict[str, Any] | None:
            """Raise a validation error."""
            raise ValueError("Props validation failed: missing required field")

    registry.register_value(ErrorMiddleware, ErrorMiddleware())
    register_middleware(registry, ErrorMiddleware)

    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    props = {"value": "test"}

    # Exception should propagate
    with pytest.raises(ValueError, match="Props validation failed"):
        execute_middleware(TestComponent, props, container)


def test_thread_safe_concurrent_middleware_execution(registry, container) -> None:
    """Test thread-safe concurrent middleware execution.

    Verifies that middleware is thread-safe when multiple threads
    execute middleware concurrently, which is critical for free-threaded Python.
    """
    tracker = ExecutionTracker()

    logging_mw = LoggingMiddleware(priority=0, tracker=tracker)

    @dataclass
    class LoggingMwType:
        priority: int = 0

        def __call__(self, comp, props, ctx):
            return logging_mw(comp, props, ctx)

    registry.register_value(LoggingMwType, LoggingMwType())
    register_middleware(registry, LoggingMwType)

    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    def execute_mw(thread_id: int) -> None:
        """Execute middleware in a thread."""
        props = {"value": f"test_{thread_id}"}
        result = execute_middleware(TestComponent, props, container)
        assert result is not None
        assert result["logged"] is True

    # Execute middleware in multiple threads
    threads = []
    num_threads = 10
    for i in range(num_threads):
        thread = threading.Thread(target=execute_mw, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all threads executed
    assert len(tracker.executions) == num_threads


def test_multiple_components_with_different_middleware(registry, container) -> None:
    """Test multiple components each with different per-component middleware.

    Verifies that per-component middleware is correctly isolated per component
    and doesn't affect other components.
    """
    tracker = ExecutionTracker()

    logging_mw = LoggingMiddleware(priority=0, tracker=tracker)

    @dataclass
    class LoggingMwType:
        priority: int = 0

        def __call__(self, comp, props, ctx):
            return logging_mw(comp, props, ctx)

    registry.register_value(LoggingMwType, LoggingMwType())
    register_middleware(registry, LoggingMwType)

    # Component 1 with transformation middleware
    transform_label = TransformationMiddleware(
        priority=5, tracker=tracker, transform_key="label"
    )

    @component(middleware={"pre_resolution": [transform_label]})
    @dataclass
    class Button:
        """Button component."""

        label: str = "Click"

    # Component 2 with transformation middleware
    transform_text = TransformationMiddleware(
        priority=5, tracker=tracker, transform_key="text"
    )

    @component(middleware={"pre_resolution": [transform_text]})
    @dataclass
    class Heading:
        """Heading component."""

        text: str = "Title"

    # Scan to register component middleware
    scan(registry, locals_dict={"Button": Button, "Heading": Heading})

    # Execute Button
    props_button = {"label": "Submit"}
    result_button = execute_middleware(Button, props_button, container)
    assert result_button is not None
    button_mw = get_component_middleware(registry, Button)
    for mw in sorted(button_mw.get("pre_resolution", []), key=lambda m: m.priority):
        result = mw(Button, result_button, container)
        assert result is not None
        result_button = cast(dict[str, Any], result)

    # Execute Heading
    props_heading = {"text": "Welcome"}
    result_heading = execute_middleware(Heading, props_heading, container)
    assert result_heading is not None
    heading_mw = get_component_middleware(registry, Heading)
    for mw in sorted(heading_mw.get("pre_resolution", []), key=lambda m: m.priority):
        result = mw(Heading, result_heading, container)
        assert result is not None
        result_heading = cast(dict[str, Any], result)

    # Verify middleware isolation
    assert result_button["label"] == "transformed_Submit"
    assert "text" not in result_button

    assert result_heading["text"] == "transformed_Welcome"
    assert "label" not in result_heading

    # Verify execution order
    expected_order = [
        "global_logging(Button)",
        "component_transform(Button)",
        "global_logging(Heading)",
        "component_transform(Heading)",
    ]
    assert tracker.executions == expected_order


def test_middleware_halt_behavior_in_integration(registry, container) -> None:
    """Test middleware halt behavior in real integration scenario.

    Verifies that when middleware returns None, execution halts properly
    and subsequent middleware (both global and per-component) doesn't run.
    """
    tracker = ExecutionTracker()

    logging_mw = LoggingMiddleware(priority=-10, tracker=tracker)
    validation_mw = ValidationMiddleware(priority=0, tracker=tracker)

    @dataclass
    class LoggingMwType:
        priority: int = -10

        def __call__(self, comp, props, ctx):
            return logging_mw(comp, props, ctx)

    @dataclass
    class ValidationMwType:
        priority: int = 0

        def __call__(self, comp, props, ctx):
            return validation_mw(comp, props, ctx)

    registry.register_value(LoggingMwType, LoggingMwType())
    registry.register_value(ValidationMwType, ValidationMwType())
    register_middleware(registry, LoggingMwType)
    register_middleware(registry, ValidationMwType)

    # Per-component middleware that should NOT run when validation halts
    transform_mw = TransformationMiddleware(
        priority=10, tracker=tracker, transform_key="label"
    )

    @component(middleware={"pre_resolution": [transform_mw]})
    @dataclass
    class Button:
        """Button component."""

        label: str = "Click"

    # Execute with invalid props
    props = {"label": "Submit", "invalid": True}
    result = execute_middleware(Button, props, container)

    # Verify execution halted at validation
    assert result is None
    assert tracker.executions == [
        "global_logging(Button)",
        "global_validation(Button)",
    ]
    # Transform middleware should NOT have executed
    assert "component_transform(Button)" not in tracker.executions


def test_lifecycle_phase_transitions(registry) -> None:
    """Test middleware execution across multiple lifecycle phases.

    Verifies that middleware can be registered for different lifecycle phases
    (pre_resolution, post_resolution, rendering) and each phase executes
    independently with its own middleware chain.
    """
    pre_tracker = ExecutionTracker()
    post_tracker = ExecutionTracker()
    rendering_tracker = ExecutionTracker()
    context: Context = cast(Context, {})

    # Different middleware for different phases
    pre_mw = LoggingMiddleware(priority=0, tracker=pre_tracker)
    post_mw = ValidationMiddleware(priority=0, tracker=post_tracker)
    rendering_mw = TransformationMiddleware(
        priority=0, tracker=rendering_tracker, transform_key="output"
    )

    @component(
        middleware={
            "pre_resolution": [pre_mw],
            "post_resolution": [post_mw],
            "rendering": [rendering_mw],
        }
    )
    @dataclass
    class TestComponent:
        """Test component with multi-phase middleware."""

        value: str = "test"

    # Scan to register component middleware
    scan(registry, locals_dict={"TestComponent": TestComponent})

    component_mw = get_component_middleware(registry, TestComponent)

    # Execute pre-resolution phase
    props = {"value": "test"}
    for mw in sorted(component_mw.get("pre_resolution", []), key=lambda m: m.priority):
        result_props = mw(TestComponent, props, context)
        assert result_props is not None
        props = cast(dict[str, Any], result_props)

    # Execute post-resolution phase
    for mw in sorted(component_mw.get("post_resolution", []), key=lambda m: m.priority):
        result_props = mw(TestComponent, props, context)
        assert result_props is not None
        props = cast(dict[str, Any], result_props)

    # Execute rendering phase
    for mw in sorted(component_mw.get("rendering", []), key=lambda m: m.priority):
        result_props = mw(TestComponent, props, context)
        assert result_props is not None
        props = cast(dict[str, Any], result_props)

    # Verify each phase executed independently
    assert pre_tracker.executions == ["global_logging(TestComponent)"]
    assert post_tracker.executions == ["global_validation(TestComponent)"]
    assert rendering_tracker.executions == ["component_transform(TestComponent)"]
