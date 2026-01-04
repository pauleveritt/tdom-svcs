"""Tests for location-based components example."""

from examples.location_based_components.app import main


def test_example_runs():
    """Test that the example runs and produces expected output."""
    result = main()

    # Verify location-based resolution works
    assert "Home: Welcome to our site!" in result
