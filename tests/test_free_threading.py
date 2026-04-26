"""
Free-threaded Python compatibility tests.

Uses pytest-run-parallel to stress-test tdom-svcs components under concurrent
access. Run with: uv run pytest tests/test_free_threading.py --parallel-threads=8

Thread-Safety Design Patterns Verified:
- Immutability: Frozen dataclasses and immutable data structures
- Atomic operations: Dict get/set operations are thread-safe
- No global state: All state is local to immutable objects
"""

from dataclasses import dataclass
from typing import Any

import pytest
from svcs_di.types import Inject
from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry
from svcs_hopscotch.middleware import Props, PropsResult, Target

from tdom_svcs import (
    execute_middleware,
    html,
    middleware,
    scan,
)


@pytest.mark.parallel_threads_limit(8)
@pytest.mark.iterations(50)
def test_html_concurrent_basic_templates():
    """Test html() with concurrent calls processing basic templates."""
    result = html(t"<div>Hello world</div>")
    assert "Hello world" in str(result)


@pytest.mark.parallel_threads_limit(8)
@pytest.mark.iterations(20)
def test_html_concurrent_with_di_container():
    """Test html() with concurrent DI container access."""

    @dataclass
    class Greeting:
        message: str = "Hello"

    @dataclass
    class GreetingComponent:
        greeting: Inject[Greeting]

        def __call__(self):
            return t"<span>{self.greeting.message}</span>"

    registry = HopscotchRegistry()
    registry.register_value(Greeting, Greeting("Hello from test"))

    with HopscotchContainer(registry) as container:
        result = html(t"<{GreetingComponent} />", container=container)
        assert "Hello from test" in str(result)


@pytest.mark.parallel_threads_limit(8)
@pytest.mark.iterations(30)
def test_html_concurrent_nested_components():
    """Test html() with concurrent nested component processing."""

    @dataclass
    class Inner:
        value: str = "inner"

        def __call__(self):
            return t"<span>{self.value}</span>"

    @dataclass
    class Outer:
        label: str = "outer"

        def __call__(self):
            return t"<div class={self.label}><{Inner} /></div>"

    result = html(t"<{Outer} />")
    assert "inner" in str(result)


@pytest.mark.parallel_threads_limit(8)
def test_middleware_concurrent_registration():
    """Test concurrent middleware registration."""
    registry = HopscotchRegistry()

    @middleware
    @dataclass
    class WorkerMiddleware:
        priority: int = 0

        def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
            return props

    scan(registry, locals_dict={"WorkerMiddleware": WorkerMiddleware})


@pytest.mark.parallel_threads_limit(8)
@pytest.mark.iterations(30)
def test_middleware_concurrent_execution():
    """Test concurrent middleware execution."""

    @middleware
    @dataclass
    class CountingMiddleware:
        priority: int = 0

        def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
            props = dict(props)
            props["processed"] = True
            return props

    @dataclass
    class TestComponent:
        pass

    registry = HopscotchRegistry()
    scan(registry, locals_dict={"CountingMiddleware": CountingMiddleware})

    with HopscotchContainer(registry) as container:
        result = execute_middleware(TestComponent, {"key": "value"}, container)
        assert result is not None
        assert result.get("processed") is True


@pytest.mark.parallel_threads_limit(8)
def test_middleware_decorator_concurrent_application():
    """Test concurrent @middleware decorator application."""

    @middleware
    @dataclass
    class WorkerMiddleware:
        priority: int = 0

        def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
            return props

    assert WorkerMiddleware is not None


@pytest.mark.parallel_threads_limit(8)
def test_scan_concurrent_operations():
    """Test concurrent scan() operations."""
    registry = HopscotchRegistry()

    @middleware
    @dataclass
    class ScanMiddleware:
        priority: int = 0

        def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
            return props

    scan(registry, locals_dict={"ScanMiddleware": ScanMiddleware})


@pytest.mark.parallel_threads_limit(8)
def test_scan_and_execute_concurrent():
    """Test end-to-end: concurrent scanning -> middleware execution."""

    @dataclass
    class TestComponent:
        pass

    @middleware
    @dataclass
    class WorkflowMiddleware:
        priority: int = 0

        def __call__(self, target: Target, props: Props, context: Any) -> PropsResult:
            props = dict(props)
            props["worker"] = True
            return props

    registry = HopscotchRegistry()
    scan(registry, locals_dict={"WorkflowMiddleware": WorkflowMiddleware})

    with HopscotchContainer(registry) as container:
        result = execute_middleware(TestComponent, {"original": True}, container)
        assert result is not None
        assert result.get("original") is True
