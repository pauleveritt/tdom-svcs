"""Tests for resource-based components example."""

from examples.resource_based_components.app import main


def test_example_runs():
    """Test that the example runs and produces expected output."""
    result = main()

    # Verify resource-based resolution works
    assert "Customer Dashboard for Alice" in result
    assert "42 visits" in result
