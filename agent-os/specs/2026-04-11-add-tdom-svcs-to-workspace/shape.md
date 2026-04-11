# Add tdom-svcs to Workspace — Shaping Notes

## Scope

Uncomment `tdom-svcs` from the root uv workspace `members` list, run `uv sync` to regenerate the lock file, then verify `uv run pytest` and `uvx ty check` pass from both the workspace root and the `tdom-svcs/` subdirectory.

This is roadmap item 18, size `S`, first task in Phase 6: Dependency Modernization.

## Decisions

- Only one line changes in the root `pyproject.toml` (uncommenting `tdom-svcs`)
- No changes needed to `tdom-svcs/pyproject.toml` — the `[tool.uv.sources]` already uses `workspace = true` (done in commit aca7263)
- `tool.ty.environment.python = "../.venv"` path should still resolve correctly after the workspace change
- No `tdom-svcs = { workspace = true }` entry needed in root `[tool.uv.sources]` — no other member currently depends on tdom-svcs
- Only `agent-verification` standard applies (no new services or tests being written)

## Context

- **Visuals:** None
- **References:** Commit `aca7263` — "Consolidate dev dependencies and sources into uv workspace root" — this commit did the prep work that makes the current change straightforward
- **Product alignment:** Phase 6: Dependency Modernization. Items 19 and 20 depend on this being completed first.

## Standards Applied

- **agent-verification** — Always included to ensure proper verification using Astral skills (`astral:uv`, `astral:ty`, `astral:ruff`) and direct pytest invocation rather than justfile recipes
