"""Tests for component discovery example."""

from examples.component_discovery.app import main


def test_example_runs():
    """Test that the example runs and produces expected output."""
    result = main()

    # Verify all components are present
    assert "<button>Click me</button>" in result
    assert "User: Alice (admin)" in result
    assert "Admin Panel" in result
    assert "42 users" in result
