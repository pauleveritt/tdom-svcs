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

from tdom_svcs.services.middleware import (
    Context,
    MiddlewareManager,
    component,
    get_component_middleware,
    setup_container,
)


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
        # Get stateful collector from context
        collector = context.get("asset_collector")
        if collector:
            collector.collect(comp_name)
        return props


# Integration tests


def test_end_to_end_workflow_with_setup_and_execution() -> None:
    """Test complete workflow: setup_container -> register -> execute -> integrate.

    This test covers the critical integration path from initial setup through
    full middleware execution with both global and per-component middleware.
    """
    # Step 1: Setup container with context
    tracker = ExecutionTracker()
    asset_collector = StatefulAssetCollector()
    context: Context = cast(Context, {"asset_collector": asset_collector})
    setup_container(context)

    # Step 2: Register global middleware
    manager = MiddlewareManager()
    manager.register_middleware(LoggingMiddleware(priority=-10, tracker=tracker))
    manager.register_middleware(ValidationMiddleware(priority=0, tracker=tracker))
    manager.register_middleware(AssetCollectionMiddleware(priority=10, tracker=tracker))

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

    # Step 4: Execute middleware for class component
    props_button = {"label": "Submit"}
    result_button = manager.execute(Button, props_button, context)

    # Execute per-component middleware
    assert result_button is not None
    component_mw = get_component_middleware(Button)
    for mw in sorted(component_mw.get("pre_resolution", []), key=lambda m: m.priority):
        result = mw(Button, result_button, context)
        assert result is not None
        # In this test, all middleware is synchronous
        result_button = cast(dict[str, Any], result)

    # Step 5: Execute middleware for function component
    props_heading = {"text": "Welcome"}
    result_heading = manager.execute(heading, props_heading, context)

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
async def test_mixed_sync_async_middleware_chain() -> None:
    """Test comprehensive mixed sync/async middleware execution.

    Verifies that sync and async middleware can be mixed in any order
    and execute correctly maintaining priority ordering.
    """
    tracker = ExecutionTracker()
    context: Context = cast(Context, {})

    manager = MiddlewareManager()
    manager.register_middleware(LoggingMiddleware(priority=-10, tracker=tracker))
    # Type checker can't detect async __call__ at static time
    manager.register_middleware(AsyncMiddleware(priority=5, tracker=tracker))  # type: ignore[arg-type]
    manager.register_middleware(ValidationMiddleware(priority=10, tracker=tracker))

    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    props = {"value": "test"}

    # Execute async chain
    result = await manager.execute_async(TestComponent, props, context)

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


def test_error_propagation_from_middleware() -> None:
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

    manager = MiddlewareManager()
    manager.register_middleware(ErrorMiddleware())

    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    props = {"value": "test"}
    context: Context = cast(Context, {})

    # Exception should propagate
    with pytest.raises(ValueError, match="Props validation failed"):
        manager.execute(TestComponent, props, context)


def test_stateful_and_stateless_middleware_together() -> None:
    """Test stateful (context-based) and stateless middleware working together.

    Demonstrates the two patterns for middleware state management:
    - Stateless: registered via MiddlewareManager
    - Stateful: stored in context and accessed by stateless middleware
    """
    tracker = ExecutionTracker()

    # Stateful middleware in context
    asset_collector = StatefulAssetCollector()
    context: Context = cast(Context, {"asset_collector": asset_collector})

    # Stateless middleware registered in manager
    manager = MiddlewareManager()
    manager.register_middleware(LoggingMiddleware(priority=-10, tracker=tracker))
    manager.register_middleware(AssetCollectionMiddleware(priority=0, tracker=tracker))

    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    props = {"value": "test"}

    result = manager.execute(TestComponent, props, context)

    # Verify both patterns worked
    assert tracker.executions == [
        "global_logging(TestComponent)",
        "asset_collection(TestComponent)",
    ]
    assert asset_collector.assets == ["TestComponent"]
    assert result is not None


def test_thread_safe_concurrent_middleware_execution() -> None:
    """Test thread-safe concurrent middleware execution.

    Verifies that MiddlewareManager is thread-safe when multiple threads
    execute middleware concurrently, which is critical for free-threaded Python.
    """
    tracker = ExecutionTracker()
    context: Context = cast(Context, {})

    manager = MiddlewareManager()
    manager.register_middleware(LoggingMiddleware(priority=0, tracker=tracker))

    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    def execute_middleware(thread_id: int) -> None:
        """Execute middleware in a thread."""
        props = {"value": f"test_{thread_id}"}
        result = manager.execute(TestComponent, props, context)
        assert result is not None
        assert result["logged"] is True

    # Execute middleware in multiple threads
    threads = []
    num_threads = 10
    for i in range(num_threads):
        thread = threading.Thread(target=execute_middleware, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify all threads executed
    assert len(tracker.executions) == num_threads


def test_multiple_components_with_different_middleware() -> None:
    """Test multiple components each with different per-component middleware.

    Verifies that per-component middleware is correctly isolated per component
    and doesn't affect other components.
    """
    tracker = ExecutionTracker()
    context: Context = cast(Context, {})

    # Global middleware
    manager = MiddlewareManager()
    manager.register_middleware(LoggingMiddleware(priority=0, tracker=tracker))

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

    # Execute Button
    props_button = {"label": "Submit"}
    result_button = manager.execute(Button, props_button, context)
    assert result_button is not None
    button_mw = get_component_middleware(Button)
    for mw in sorted(button_mw.get("pre_resolution", []), key=lambda m: m.priority):
        # In this test, all middleware is synchronous
        result = mw(Button, result_button, context)
        assert result is not None
        result_button = cast(dict[str, Any], result)

    # Execute Heading
    props_heading = {"text": "Welcome"}
    result_heading = manager.execute(Heading, props_heading, context)
    assert result_heading is not None
    heading_mw = get_component_middleware(Heading)
    for mw in sorted(heading_mw.get("pre_resolution", []), key=lambda m: m.priority):
        # In this test, all middleware is synchronous
        result = mw(Heading, result_heading, context)
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


def test_middleware_halt_behavior_in_integration() -> None:
    """Test middleware halt behavior in real integration scenario.

    Verifies that when middleware returns None, execution halts properly
    and subsequent middleware (both global and per-component) doesn't run.
    """
    tracker = ExecutionTracker()
    context: Context = cast(Context, {})

    # Global middleware that halts on invalid props
    manager = MiddlewareManager()
    manager.register_middleware(LoggingMiddleware(priority=-10, tracker=tracker))
    manager.register_middleware(ValidationMiddleware(priority=0, tracker=tracker))

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
    result = manager.execute(Button, props, context)

    # Verify execution halted at validation
    assert result is None
    assert tracker.executions == [
        "global_logging(Button)",
        "global_validation(Button)",
    ]
    # Transform middleware should NOT have executed
    assert "component_transform(Button)" not in tracker.executions


def test_lifecycle_phase_transitions() -> None:
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

    component_mw = get_component_middleware(TestComponent)

    # Execute pre-resolution phase
    props = {"value": "test"}
    for mw in sorted(component_mw.get("pre_resolution", []), key=lambda m: m.priority):
        result_props = mw(TestComponent, props, context)

        assert result_props is not None

        # In this test, all middleware is synchronous
        props = cast(dict[str, Any], result_props)

    # Execute post-resolution phase
    for mw in sorted(component_mw.get("post_resolution", []), key=lambda m: m.priority):
        result_props = mw(TestComponent, props, context)

        assert result_props is not None

        # In this test, all middleware is synchronous
        props = cast(dict[str, Any], result_props)

    # Execute rendering phase
    for mw in sorted(component_mw.get("rendering", []), key=lambda m: m.priority):
        result_props = mw(TestComponent, props, context)

        assert result_props is not None

        # In this test, all middleware is synchronous
        props = cast(dict[str, Any], result_props)

    # Verify each phase executed independently
    assert pre_tracker.executions == ["global_logging(TestComponent)"]
    assert post_tracker.executions == ["global_validation(TestComponent)"]
    assert rendering_tracker.executions == ["component_transform(TestComponent)"]


def test_middleware_with_context_service_injection() -> None:
    """Test middleware retrieving services from context.

    Verifies that middleware can access services stored in the context
    using the Context protocol's dict-like interface.
    """
    pytest.importorskip("svcs")
    import svcs

    tracker = ExecutionTracker()

    # Create svcs container with services
    registry = svcs.Registry()

    @dataclass
    class Logger:
        """Logger service."""

        name: str

    registry.register_value(Logger, Logger(name="test-logger"))
    container = svcs.Container(registry)

    # Middleware that uses service from context
    @dataclass
    class ServiceAwareMiddleware:
        """Middleware that retrieves service from context."""

        priority: int
        tracker: ExecutionTracker

        def __call__(
            self,
            component: type | Callable[..., Any],
            props: dict[str, Any],
            context: Context,
        ) -> dict[str, Any] | None:
            """Use logger service from context."""
            # Context protocol provides dict-like access
            logger = context.get(Logger)  # type: ignore[arg-type]
            comp_name = (
                component.__name__ if hasattr(component, "__name__") else str(component)
            )
            self.tracker.record(f"logged_by_{logger.name}({comp_name})")
            props["logger_name"] = logger.name
            return props

    manager = MiddlewareManager()
    manager.register_middleware(ServiceAwareMiddleware(priority=0, tracker=tracker))

    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    props = {"value": "test"}
    result = manager.execute(TestComponent, props, cast(Context, container))

    # Verify service was retrieved and used
    assert tracker.executions == ["logged_by_test-logger(TestComponent)"]
    assert result is not None
    assert result["logger_name"] == "test-logger"


def test_performance_stress_with_many_middleware() -> None:
    """Test middleware performance under load with many middleware instances.

    Verifies that middleware system performs adequately with many registered
    middleware and components. This is a basic stress test, not a benchmark.
    """
    context: Context = cast(Context, {})

    # Create many middleware instances
    manager = MiddlewareManager()
    num_middleware = 50
    for i in range(num_middleware):

        @dataclass
        class StressTestMiddleware:
            """Middleware for stress testing."""

            priority: int = i
            index: int = i

            def __call__(
                self,
                component: type | Callable[..., Any],
                props: dict[str, Any],
                context: Context,
            ) -> dict[str, Any] | None:
                """Simple props passthrough."""
                props[f"mw_{self.index}"] = True
                return props

        manager.register_middleware(StressTestMiddleware(priority=i, index=i))

    @dataclass
    class TestComponent:
        """Test component."""

        value: str = "test"

    # Execute many times to simulate load
    start_time = time.time()
    num_executions = 1000
    for _ in range(num_executions):
        props = {"value": "test"}
        result = manager.execute(TestComponent, props, context)
        assert result is not None

    elapsed = time.time() - start_time

    # Verify execution completed (basic assertion, not strict performance requirement)
    # Should complete 1000 executions with 50 middleware in reasonable time
    assert elapsed < 5.0, f"Stress test took {elapsed:.2f}s, expected < 5s"

    # Verify all middleware executed
    assert len([k for k in result.keys() if k.startswith("mw_")]) == num_middleware
