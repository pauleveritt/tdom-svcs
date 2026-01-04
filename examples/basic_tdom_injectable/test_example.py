import pytest

from examples.basic_tdom_injectable.app import main


@pytest.mark.skip(reason="Template DI not yet implemented - Button requires Inject[Counter]")
def test_main():
    result = main()
    assert 'class="dashboard"' in result
    assert "Welcome, Alice!" in result
