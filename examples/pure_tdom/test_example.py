from examples.pure_tdom.app import main


def test_example_runs():
    """Test that the example runs and produces expected output."""
    result = main()

    assert "Hello, Alice!" in result
    assert "admin" in result
