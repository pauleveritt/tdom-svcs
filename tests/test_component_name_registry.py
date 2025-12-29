"""
Tests for ComponentNameRegistry service.

This module tests the ComponentNameRegistry service which maps component
string names to type objects for component resolution.
"""

import threading
from typing import Any

import pytest

from tdom_svcs.services import ComponentNameRegistry


# Test fixtures - class component types (only classes can be registered by name)
from dataclasses import dataclass


@dataclass
class Button:
    """Simple button component."""

    label: str = "Click"

    def __call__(self) -> str:
        return f"<button>{self.label}</button>"


@dataclass
class Card:
    """Simple card component."""

    title: str = "Card"

    def __call__(self) -> str:
        return f"<div>{self.title}</div>"


class AlertComponent:
    """Class-based component."""

    def __init__(self, *, message: str = "Alert"):
        self.message = message

    def __call__(self) -> str:
        return f"<div>{self.message}</div>"


def test_register_and_retrieve_component_type():
    """Test basic registration and retrieval of component type."""
    registry = ComponentNameRegistry()

    # Register a component
    registry.register("Button", Button)

    # Retrieve the component type
    result = registry.get_type("Button")
    assert result is Button


def test_get_type_returns_none_for_unregistered_name():
    """Test that get_type returns None for unregistered component names."""
    registry = ComponentNameRegistry()

    # Try to retrieve unregistered component
    result = registry.get_type("NonExistent")
    assert result is None


def test_get_all_names_returns_registered_names():
    """Test that get_all_names returns list of all registered component names."""
    registry = ComponentNameRegistry()

    # Register multiple components
    registry.register("Button", Button)
    registry.register("Card", Card)
    registry.register("Alert", AlertComponent)

    # Get all names
    names = registry.get_all_names()

    assert isinstance(names, list)
    assert set(names) == {"Button", "Card", "Alert"}


def test_register_overwrites_existing_registration():
    """Test that registering a name twice overwrites the previous registration."""
    registry = ComponentNameRegistry()

    # Register Button
    registry.register("Button", Button)
    assert registry.get_type("Button") is Button

    # Register a different type with the same name
    registry.register("Button", Card)
    assert registry.get_type("Button") is Card


def test_get_all_names_returns_empty_list_for_empty_registry():
    """Test that get_all_names returns empty list when no components registered."""
    registry = ComponentNameRegistry()

    names = registry.get_all_names()
    assert names == []


@pytest.mark.freethreaded
def test_concurrent_registration_and_retrieval():
    """Test thread-safe concurrent registration and retrieval of components."""
    registry = ComponentNameRegistry()
    errors: list[Exception] = []
    results: list[tuple[str, Any]] = []

    def register_worker(name: str, component_type: type) -> None:
        """Worker thread that registers a component multiple times."""
        try:
            for i in range(50):
                registry.register(f"{name}_{i}", component_type)
        except Exception as e:
            errors.append(e)

    def retrieve_worker(name: str) -> None:
        """Worker thread that retrieves components."""
        try:
            for i in range(50):
                result = registry.get_type(f"{name}_{i}")
                results.append((f"{name}_{i}", result))
        except Exception as e:
            errors.append(e)

    # Spawn threads for concurrent registration
    threads = []
    for i in range(4):
        threads.append(
            threading.Thread(target=register_worker, args=(f"Comp{i}", Button))
        )

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Spawn threads for concurrent retrieval
    retrieval_threads = []
    for i in range(4):
        retrieval_threads.append(
            threading.Thread(target=retrieve_worker, args=(f"Comp{i}",))
        )

    for t in retrieval_threads:
        t.start()
    for t in retrieval_threads:
        t.join()

    # Check no errors occurred
    assert len(errors) == 0, f"Errors during concurrent access: {errors}"

    # Verify we got results (at least some should have been retrieved)
    assert len(results) > 0

    # Verify all registered components can be retrieved
    for i in range(4):
        for j in range(50):
            name = f"Comp{i}_{j}"
            assert registry.get_type(name) is Button


@pytest.mark.freethreaded
def test_concurrent_get_all_names():
    """Test thread-safe concurrent access to get_all_names."""
    registry = ComponentNameRegistry()
    errors: list[Exception] = []
    all_names: list[list[str]] = []

    # Pre-register some components
    for i in range(10):
        registry.register(f"Component_{i}", Button)

    def get_names_worker() -> None:
        """Worker thread that retrieves all names."""
        try:
            for _ in range(50):
                names = registry.get_all_names()
                all_names.append(names)
        except Exception as e:
            errors.append(e)

    # Spawn multiple threads
    threads = [threading.Thread(target=get_names_worker) for _ in range(8)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Check no errors occurred
    assert len(errors) == 0, f"Errors during concurrent access: {errors}"

    # Verify we got results
    assert len(all_names) > 0

    # All results should contain the registered names
    expected_names = {f"Component_{i}" for i in range(10)}
    for names in all_names:
        assert set(names) == expected_names
