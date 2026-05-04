# tdom-svcs Agent OS Migration Pilot Plan

## Purpose

Migrate `tdom-svcs` Agent OS artifacts to native Superpowers-oriented files
using the repeatable process proven in `svcs-di`.

## Inputs

- Inventory: `docs/superpowers/migration-inventory.md`
- Legacy source: `agent-os/`
- Local Agent OS commands: `.claude/commands/agent-os/`
- Research docs: `docs/research/`

## Task 1: Establish Native Superpowers Skeleton

Status: complete for the first preservation pass.

Create the target folders needed for migrated content:

- `docs/superpowers/specs/`
- `docs/superpowers/plans/`
- `docs/superpowers/product/`

No Agent OS files are deleted in this task.

## Task 2: Preserve Product Context

Status: complete for the first preservation pass.

Copy product content into `docs/superpowers/`:

- `agent-os/product/mission.md` to `docs/superpowers/product/mission.md`
- `agent-os/product/roadmap.md` to `docs/superpowers/roadmap.md`
- `agent-os/product/tech-stack.md` to `docs/superpowers/product/tech-stack.md`

## Task 3: Preserve Historical Specs

Status: complete for the first preservation pass.

Copy all `agent-os/specs/*` directories into `docs/superpowers/specs/`,
preserving old and new artifact shapes.

Acceptance:

- All 15 Agent OS spec directories exist under `docs/superpowers/specs/`.
- File counts match the Agent OS source inventory.
- No `agent-os/specs/` deletion happens until verification passes.

## Task 4: Record Standards Decisions

Status: complete from the shared migration decisions.

The local standards match the standards already classified in the `svcs-di`
pilot. Useful content has been migrated to root Superpowers policies or Codex
skills; Agent OS-only discovery scaffolding is marked for deletion.

## Task 5: Docs Integration

Status: complete for the preservation pass.

`tdom-svcs` has no `docs/specifications/` wrapper tree, so this task should
verify that docs do not depend on `agent-os/`. If Sphinx discovers
`docs/superpowers/**` as orphan pages, exclude that tree from source discovery
until the future Superpowers Sphinx plugin exists.

`docs/conf.py` now excludes `superpowers/**` from Sphinx source discovery.

## Task 6: Remove Agent OS Tooling Residue

Status: complete.

After content migration and docs verification:

- delete `.claude/commands/agent-os/`
- delete `agent-os/`
- remove live references to Agent OS from package docs, except historical notes
  where useful

## Task 7: Verify

Status: complete with recorded exceptions.

Run package checks using workspace-approved tools:

```bash
just docs
just quality
just test
```

If a recipe is absent, use the closest package-local recipe and record the
exception.

Known exception: `just docs-build` currently fails due pre-existing
example/research warnings unrelated to Agent OS. The migration resolved the
additional `docs/superpowers/**` orphan warnings by excluding that tree from
Sphinx source discovery.

Verification status on 2026-05-04:

- `just docs-build`: fails with pre-existing example/research warnings.
- `just quality`: Ruff check and format check pass; `ty check` fails with two
  pre-existing `register_middleware(...)` argument diagnostics in
  `examples/categories/categories_example.py` and `tests/test_categories.py`.
- `just test`: passes with 93 passed and 18 skipped.

Follow-up cleanup: removed the stale `agent-os` exclusion from `pyproject.toml`
after the Agent OS directory was deleted.
