# Roadmap Partitioning Policy

This policy defines how Superpowers packages maintain roadmaps as three companion files without changing the existing roadmap row columns.

## File Roles

- `docs/superpowers/roadmap.md` is the execution view. It keeps rows with status `next`, `active`, and `blocked`.
- `docs/superpowers/roadmap-backlog.md` is the backlog view. It keeps rows with status `future`, `partial`, and any legacy `deferred` rows that have not been normalized yet.
- `docs/superpowers/roadmap-archive.md` is the historical record. It keeps rows with status `done`, `done (deferred)`, and `retired`.
- A roadmap row lives in exactly one of these files at a time.

## Grouping Convention

- Use `## Phase: <name>` section headers to group execution-scope rows in `docs/superpowers/roadmap.md`.
- Keep the existing roadmap table columns unchanged.
- Express parallel work with `‖` markers in `Depends On`, alongside one short prose note above the table.
- Express sequencing with `→` markers in `Depends On`, and keep blockers in the existing `Depends On` and `Acceptance Signal` columns rather than by adding a new schema column.
- Backlog and archive files may also use section headers when that improves scanability, but they do not need the same phase prose as the execution view.

## Movement Rules

- When a row becomes active planning or execution work, move it into `docs/superpowers/roadmap.md` with one of the execution statuses.
- When work is landed in part but no longer belongs in the short execution view, move it to `docs/superpowers/roadmap-backlog.md` with status `partial`.
- When a row is explicitly delayed, long-horizon, or waiting for a later cycle, move it to `docs/superpowers/roadmap-backlog.md` and mark it `future` or `deferred`.
- When a row is verified complete, move it to `docs/superpowers/roadmap-archive.md` and mark it `done` or `done (deferred)` as appropriate.
- When a row is intentionally abandoned, superseded, or closed as no longer worth pursuing, move it to `docs/superpowers/roadmap-archive.md` and mark it `retired`.
- Do not leave duplicate copies behind when moving a row between files.

## Docs Indexing And Tooling

- The docs index should expose all three roadmap companions so readers can navigate execution scope, backlog, and archive directly.
- Human and agent tooling that adds or updates roadmap rows must route by status to the correct companion file.
- This policy is the source of truth for how the split works when a command or older note disagrees.

## Superpowers Scope

This three-file structure is adopted across Superpowers packages in the t-strings workspace. See individual package roadmaps for the current execution scope, backlog, and historical record.
