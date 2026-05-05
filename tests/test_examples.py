"""Tests that verify all examples work correctly."""

from types import ModuleType

import pytest

from tainie_tools.fixtures import ExampleRunner


def test_example_runs_without_error(
    example_module: ModuleType,
    run_example: ExampleRunner,
) -> None:
    if not hasattr(example_module, "main"):
        pytest.skip(f"No main() in {example_module.__name__}")
    run_example(example_module)
