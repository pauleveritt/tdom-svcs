# References for Add tdom-svcs to Workspace

## Similar Implementations

### Commit aca7263 — Consolidate dev dependencies and sources into uv workspace root

- **Location:** `git show aca7263` in the `tdom-svcs` repo
- **Relevance:** This commit was the prep work for the current task. It converted `tdom-svcs/pyproject.toml`'s `[tool.uv.sources]` from `path = "...", editable = true` entries to `workspace = true`, and trimmed dev dependencies that were moved to the workspace root. The current task is the natural follow-up: actually adding `tdom-svcs` to the workspace members list.
- **Key patterns:** The pattern established here — workspace members use `{ workspace = true }` sources and keep only package-specific dev deps locally — is what tdom-svcs already follows.

### svcs-di workspace member configuration

- **Location:** `/Users/pauleveritt/projects/t-strings/svcs-di/pyproject.toml`
- **Relevance:** `svcs-di` is the closest peer to `tdom-svcs` in the workspace: both depend on workspace packages, both use `tool.ty.environment.python = "../.venv"`, both use `uv_build`. It's the model for what a correctly configured workspace member looks like.
- **Key patterns:** No local `[tool.uv.sources]` section (relies on root), `python = "../.venv"` in ty environment, `requires-python = ">=3.14"`.

### Workspace root pyproject.toml

- **Location:** `/Users/pauleveritt/projects/t-strings/pyproject.toml`
- **Relevance:** The file with the commented-out `tdom-svcs` entry. Current workspace members: `aria-testing`, `svcs-di`, `svcs-hopscotch`, `tstring-html`. Root `[tool.uv.sources]` maps `aria-testing`, `tdom`, `svcs-di`, `svcs-hopscotch` to `{ workspace = true }`.
