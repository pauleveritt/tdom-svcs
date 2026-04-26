# Standards for Cleanup Container-Only Context

## agent-verification

**How agents should verify code** — Use Astral skills directly, not justfile recipes.

### Type Checking

- Use the `astral:ty` skill to check types and get guidance
- Pay attention to ty LSP diagnostics
- Read and understand type errors before attempting fixes

### Linting and Formatting

- Use the `astral:ruff` skill to check, format, and fix code
- Let ruff guide you on style and error fixes

### Testing

- Use `uv run pytest tests/` directly with clear descriptions
- Use `astral:uv` skill if you need guidance on pytest or uv usage
- Specify test paths clearly

### Why

- **Justfile recipes** are convenience wrappers for humans and CI/CD
- **Astral skills** provide richer context and guidance for agents
- **Direct tool usage** gives better error messages and actionable diagnostics
- **Skills can provide guidance** on how to fix issues, not just report them

---

## testing/function-based-tests

**Write tests as functions, never classes.**

### Correct Pattern

```python
def test_user_can_login_with_valid_credentials():
    """Test successful login."""
    user = create_user(password="secret")
    assert user.login("secret") is True

def test_user_cannot_login_with_wrong_password():
    """Test login failure."""
    user = create_user(password="secret")
    assert user.login("wrong") is False
```

### Why Functions

- Simpler, less boilerplate
- No `self` parameter noise
- Fixtures work more naturally
- Pytest's native style

### Rules

- Name: `test_<what>_<scenario>()`
- One assertion focus per test
- Use fixtures for shared setup, not class `setUp`

**Relevance to this item:** We're updating and deleting function-based tests. All changes follow this standard.
