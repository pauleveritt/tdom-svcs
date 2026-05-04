# Standards for Migrate Template Return Types

## agent-verification

Use Astral skills directly — not justfile recipes.

- Type checking: `astral:ty` skill
- Linting/formatting: `astral:ruff` skill  
- Testing: `uv run pytest tests/` directly

## testing/function-based-tests

Write tests as functions, never classes. Name: `test_<what>_<scenario>()`.
All component definitions inside tests should follow the new Template pattern.
