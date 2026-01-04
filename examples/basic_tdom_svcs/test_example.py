from examples.basic_tdom_svcs.app import main


def test_example_runs():
    """Test that the example runs and produces expected output."""
    result = main()

    assert "Hello from tdom_svcs!" in result
    assert "Users: 3" in result
