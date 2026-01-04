from examples.middleware.app import main


def test_example_runs():
    """Test that the example runs and produces expected output."""
    result = main()

    assert "Submit" in result
