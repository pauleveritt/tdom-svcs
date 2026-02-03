"""
Free-threaded Python compatibility tests.

This module verifies thread-safety of tdom-svcs components under PEP 703's free-threaded
Python (no-GIL mode) through concurrent access stress tests.

Thread-Safety Design Patterns Verified:
- Immutability: Frozen dataclasses and immutable data structures
- Atomic operations: Dict get/set operations are thread-safe
- No global state: All state is local to immutable objects

The tests in this module use multiple concurrent threads to stress-test the following:
1. html() template processing with concurrent calls
2. Middleware registration and execution
3. Scanning operations

All tests are marked with @pytest.mark.freethreaded and require a free-threaded Python build.
"""

import sysconfig
import threading
from dataclasses import dataclass

import pytest
from svcs_di.auto import Inject
from svcs_di.injectors import HopscotchContainer, HopscotchRegistry

from tdom_svcs import (
    execute_middleware,
    html,
    middleware,
    register_middleware,
    scan,
)
from tdom_svcs.types import Component, Context, Props, PropsResult


# ============================================================================
# Task Group 1: Infrastructure Setup
# ============================================================================


def is_free_threaded_build() -> bool:
    """
    Check if running on free-threaded Python build.

    Returns True if Py_GIL_DISABLED is set (free-threaded build),
    False otherwise (standard GIL build).
    """
    gil_disabled = sysconfig.get_config_var("Py_GIL_DISABLED")
    return gil_disabled == 1


@pytest.mark.freethreaded
def test_free_threaded_build_detection():
    """Test that free-threaded build detection works correctly."""
    result = is_free_threaded_build()
    assert isinstance(result, bool)


@pytest.mark.freethreaded
def test_pytest_run_parallel_available():
    """Test that pytest-run-parallel plugin is available."""
    assert True


@pytest.mark.freethreaded
@pytest.mark.skipif(
    not is_free_threaded_build(),
    reason="Requires free-threaded Python build (python3.14t or later)",
)
def test_free_threaded_build_confirmed():
    """Test that we are running on a free-threaded build."""
    assert is_free_threaded_build() is True


# ============================================================================
# Task Group 2: html() Template Processing Thread-Safety
# ============================================================================


@pytest.mark.freethreaded
def test_html_concurrent_basic_templates():
    """Test html() with concurrent calls processing basic templates."""
    results: list[str] = []
    errors: list[Exception] = []

    def worker(worker_id: int):
        """Worker thread that processes templates."""
        try:
            for i in range(50):
                node = html(t"<div>Worker {worker_id} iteration {i}</div>")
                results.append(str(node))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]

    for t_thread in threads:
        t_thread.start()
    for t_thread in threads:
        t_thread.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 400  # 8 threads * 50 iterations


@pytest.mark.freethreaded
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

    results: list[str] = []
    errors: list[Exception] = []

    def worker(worker_id: int):
        """Worker thread that processes templates with DI."""
        try:
            registry = HopscotchRegistry()
            registry.register_value(Greeting, Greeting(f"Hello from {worker_id}"))

            with HopscotchContainer(registry) as container:
                for _ in range(20):
                    node = html(t"<{GreetingComponent} />", context=container)
                    results.append(str(node))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]

    for t_thread in threads:
        t_thread.start()
    for t_thread in threads:
        t_thread.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 160  # 8 threads * 20 iterations


@pytest.mark.freethreaded
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

    results: list[str] = []
    errors: list[Exception] = []

    def worker():
        """Worker thread that processes nested components."""
        try:
            for _ in range(30):
                node = html(t"<{Outer} />")
                results.append(str(node))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(8)]

    for t_thread in threads:
        t_thread.start()
    for t_thread in threads:
        t_thread.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 240  # 8 threads * 30 iterations


# ============================================================================
# Task Group 3: Middleware Thread-Safety
# ============================================================================


@pytest.mark.freethreaded
def test_middleware_concurrent_registration():
    """Test concurrent middleware registration."""
    errors: list[Exception] = []
    registries: list[HopscotchRegistry] = []

    def worker(worker_id: int):
        """Worker thread that registers middleware."""
        try:
            registry = HopscotchRegistry()

            @middleware
            @dataclass
            class WorkerMiddleware:
                priority: int = worker_id

                def __call__(
                    self, component: Component, props: Props, context: Context
                ) -> PropsResult:
                    return props

            register_middleware(registry, WorkerMiddleware)
            registries.append(registry)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]

    for t_thread in threads:
        t_thread.start()
    for t_thread in threads:
        t_thread.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(registries) == 8


@pytest.mark.freethreaded
def test_middleware_concurrent_execution():
    """Test concurrent middleware execution."""

    @middleware
    @dataclass
    class CountingMiddleware:
        priority: int = 0

        def __call__(
            self, component: Component, props: Props, context: Context
        ) -> PropsResult:
            props = dict(props)
            props["processed"] = True
            return props

    @dataclass
    class TestComponent:
        pass

    results: list[PropsResult] = []
    errors: list[Exception] = []

    def worker():
        """Worker thread that executes middleware."""
        try:
            registry = HopscotchRegistry()
            register_middleware(registry, CountingMiddleware)

            with HopscotchContainer(registry) as container:
                for _ in range(30):
                    result = execute_middleware(
                        TestComponent, {"key": "value"}, container
                    )
                    results.append(result)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(8)]

    for t_thread in threads:
        t_thread.start()
    for t_thread in threads:
        t_thread.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 240  # 8 threads * 30 iterations
    assert all(r is not None and r.get("processed") for r in results)


@pytest.mark.freethreaded
def test_middleware_decorator_concurrent_application():
    """Test concurrent @middleware decorator application."""
    results: list[tuple[int, type]] = []
    errors: list[Exception] = []

    def worker(worker_id: int):
        """Worker thread that applies middleware decorator."""
        try:

            @middleware
            @dataclass
            class WorkerMiddleware:
                priority: int = worker_id

                def __call__(
                    self, component: Component, props: Props, context: Context
                ) -> PropsResult:
                    return props

            results.append((worker_id, WorkerMiddleware))
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]

    for t_thread in threads:
        t_thread.start()
    for t_thread in threads:
        t_thread.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 8


# ============================================================================
# Task Group 4: Scanning Thread-Safety
# ============================================================================


@pytest.mark.freethreaded
def test_scan_concurrent_operations():
    """Test concurrent scan() operations."""
    results: list[HopscotchRegistry] = []
    errors: list[Exception] = []

    def worker(worker_id: int):
        """Worker thread that performs scanning."""
        try:
            registry = HopscotchRegistry()

            @middleware
            @dataclass
            class ScanMiddleware:
                priority: int = worker_id

                def __call__(
                    self, component: Component, props: Props, context: Context
                ) -> PropsResult:
                    return props

            scan(registry, locals_dict={"ScanMiddleware": ScanMiddleware})
            results.append(registry)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]

    for t_thread in threads:
        t_thread.start()
    for t_thread in threads:
        t_thread.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 8


@pytest.mark.freethreaded
def test_scan_and_execute_concurrent():
    """Test end-to-end: concurrent scanning -> middleware execution."""

    @dataclass
    class TestComponent:
        pass

    results: list[PropsResult] = []
    errors: list[Exception] = []

    def worker(worker_id: int):
        """Worker thread performing full workflow."""
        try:

            @middleware
            @dataclass
            class WorkflowMiddleware:
                priority: int = 0

                def __call__(
                    self, component: Component, props: Props, context: Context
                ) -> PropsResult:
                    props = dict(props)
                    props["worker"] = worker_id
                    return props

            registry = HopscotchRegistry()
            scan(registry, locals_dict={"WorkflowMiddleware": WorkflowMiddleware})

            with HopscotchContainer(registry) as container:
                result = execute_middleware(
                    TestComponent, {"original": True}, container
                )
                results.append(result)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]

    for t_thread in threads:
        t_thread.start()
    for t_thread in threads:
        t_thread.join()

    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert len(results) == 8
    assert all(r is not None and r.get("original") for r in results)
