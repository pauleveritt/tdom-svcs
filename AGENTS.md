# tdom-svcs

TDOM integration with svcs dependency injection.

## Authoring Boundary

Keep `from tdom_svcs import html` as the obvious first move. Context and
dependency injection should be additive affordances for larger component trees,
not mandatory setup before rendering ordinary HTML.

## Workflow

- Do not automatically commit when implementing a plan; allow review unless the
  user explicitly asks for commits.
