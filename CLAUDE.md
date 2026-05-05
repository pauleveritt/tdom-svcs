# Claude Code Instructions

## Project

Experimental research project integrating svcs dependency injection with tdom. Breaking changes are
encouraged—prioritize best design over backwards compatibility.

## Tooling

Use Astral tools: `uv` (package manager), `ruff` (linter/formatter), `ty` (type checker and Python LSP)

## Workflow

- Don't automatically commit when you implement a plan, allow review

## Authoring Boundary

Keep `from tdom_svcs import html` as the obvious first move. Context and
dependency injection should be additive affordances for larger component trees,
not mandatory setup before rendering ordinary HTML.
