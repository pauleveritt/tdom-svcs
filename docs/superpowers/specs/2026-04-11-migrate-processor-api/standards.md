# Standards for Migrate Processor Off the Node-Based API

The following standards apply to this work.

---

## agent-verification (ALWAYS INCLUDED)

### Purpose

Agents should use Astral tools directly via skills rather than convenience wrappers like justfile recipes. This ensures agents get the full context and guidance these tools provide.

### Rationale

- **Justfile recipes** (`just test`, `just lint`) are convenience wrappers for humans and CI/CD
- **Astral skills** (`astral:ruff`, `astral:ty`, `astral:uv`) provide richer context and guidance for agents
- **Direct tool usage** gives better error messages and actionable diagnostics
- **ty LSP** provides real-time type checking feedback during development
- **Skills can provide guidance** on how to fix issues, not just report them

### Rules for Verification

#### Type Checking

**DO:**
- Use the `astral:ty` skill to check types and get guidance
- Pay attention to ty LSP diagnostics as they appear in tool results
- Read and understand type errors before attempting fixes

**DON'T:**
- Run `just lint` or `just typecheck` through Bash
- Ignore ty diagnostics that appear during development

#### Linting and Formatting

**DO:**
- Use the `astral:ruff` skill to check, format, and fix code
- Let ruff guide you on style and error fixes

**DON'T:**
- Run `just lint` or `just format` through Bash
- Apply fixes without understanding what ruff is correcting

#### Testing

**DO:**
- Use `uv run pytest` directly with clear descriptions
- Use `astral:uv` skill if you need guidance on pytest or uv usage
- Specify test paths clearly (e.g., `uv run pytest tests/` not `just test`)

**DON'T:**
- Run `just test` through Bash
- Use justfile test recipes in verification steps

#### Package Management

**DO:**
- Use the `astral:uv` skill for dependency management and guidance
- Run `uv` commands directly when the operation is clear

**DON'T:**
- Run uv commands through bash without understanding the operation
- Skip using the skill when you need guidance on uv features
