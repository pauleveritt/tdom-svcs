# Migrate Template Return Types — Shaping Notes

## Scope

Make every component `__call__` method return `Template` (`t"..."`) directly instead of
`str | Markup`. Covers tdom-svcs examples/tests and themester source/examples/tests.
The processor already handles both return types; zero behavior change in rendered output.

## Decisions

- **Template return only**: Components return `t"..."` not `html(t"...")`. Inner html() calls removed.
- **context= param removed**: Views/components no longer accept `context=` parameter.
  DI goes through `Inject[T]` fields.
- **get_view() stays returning str**: Calls `html(template, container=container)` internally.
- **Complex cases (Navbar with AssetCollector)**: Drop `context=` param; switch to
  `Inject[AssetCollector]` field if the example wires it, or defer if not.
- **Processor unchanged**: `str | Markup` support stays during migration window (Stage 3 removes it).

## Context

- **Visuals:** None
- **References:** `tdom-svcs/docs/research/port-tstring-html-integrations.md` Stage 2
- **Product alignment:** Phase 7, item 23 on roadmap

## Standards Applied

- `agent-verification` — Astral skills for verification
- `testing/function-based-tests` — Tests are functions
