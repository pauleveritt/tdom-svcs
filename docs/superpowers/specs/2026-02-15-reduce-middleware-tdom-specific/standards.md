# Standards Applied

## agent-verification

Use automated tools for verification:
- `astral:ruff` skill for linting and formatting
- `astral:ty` skill for type checking
- `uv run pytest` for test execution
- `grep` for finding remaining imports from deleted modules

## testing/function-based-tests

Keep integration tests simple and function-based. Don't use test classes unnecessarily.

Example from `test_categories.py`:
```python
def test_middleware_decorator_sets_category():
    """@middleware re-export should set category metadata."""
    # Simple function-based test
    ...
```

## testing/fakes-over-mocks

Prefer real Registry instances and actual middleware functions in tests rather than mocking:

```python
# Good: Use real objects
registry = svcs.Registry()
registry.register_value(SomeService, instance)

# Avoid: Excessive mocking
mock_registry = Mock()
mock_registry.get.return_value = Mock()
```

For this refactoring, most tests will use real svcs Registry and real middleware functions.
