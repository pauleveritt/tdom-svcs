# Complete Example Bundle Migration Design

Date: 2026-05-06

## Summary

Migrate all remaining `tdom-svcs` example docs from brittle Sphinx
`literalinclude` anchors to the `tainie-tools` example bundle directives:
`example-snippet` and `example-source`.

The work should start simple but finish the full `docs/examples/**` surface
before leaving roadmap item 48. The migration should proceed in grouped passes:

1. inventory remaining `literalinclude` usage;
2. migrate Basic examples;
3. migrate Categories examples;
4. migrate Hopscotch examples;
5. migrate Middleware examples;
6. verify generated `example-inventory.json` and mark the roadmap item complete.

## Context

`tainie-tools` Example Bundle Authoring has landed and is already enabled in
`docs/conf.py` through:

```python
extensions = [
    "tainie_tools.examples.sphinx",
]

tainie_examples_dir = "../examples"
tainie_examples_inventory_path = "example-inventory.json"
```

`docs/examples/hopscotch/resource.md` is the current pilot. It already uses
`example-snippet` and `example-source` for most of the page and has
`examples/hopscotch/resource/example.toml`.

The remaining docs still contain many `literalinclude` blocks, especially with
`:start-at:` and `:end-at:` anchors. Those anchors are fragile because prose
changes in example source files can silently break docs.

## Recommended Approach

Use a grouped full migration.

Single-file examples should stay lightweight:

- add `# docs: start <snippet-id>` and `# docs: end <snippet-id>` markers around
  stable sections in the example `.py` file;
- replace page-local `literalinclude` blocks with `example-snippet`;
- use `example-source` for full source listings.

Directory examples should use an `example.toml` manifest:

- Hopscotch multi-file examples;
- Middleware ARIA example.

Each manifest should include:

- `id`;
- `title`;
- `summary`;
- `entrypoint`;
- `concepts` and `proves` only when the page clearly maps to known domain ids.

## Scope

In scope:

- all current pages under `docs/examples/**`;
- all example files under `examples/**` needed for snippet markers;
- `example.toml` manifests for multi-file bundles;
- small doc wording adjustments where replacing literal includes requires a
  cleaner snippet boundary;
- roadmap item 48 completion after verification.

Out of scope:

- restructuring the published docs navigation;
- README rewrite;
- new example behavior;
- new `tainie-tools` directive features;
- changing rendered example output.

## Migration Order

### 1. Inventory

Build a table of remaining `literalinclude` blocks with:

- docs page path;
- referenced example file;
- whether it uses `:start-at:` or `:end-at:`;
- whether it should become a snippet or full source listing;
- whether the backing example is single-file or bundle-based.

This table can live in the implementation plan rather than as a permanent repo
artifact.

### 2. Basic

Migrate:

- `docs/examples/basic/pure_tdom.md`;
- `docs/examples/basic/function_dataclass_poco.md`;
- `docs/examples/basic/svcs_container.md`;
- `docs/examples/basic/inject_service.md`;
- `docs/examples/basic/props_priority.md`.

These should mostly be single-file examples with direct source ids such as
`pure_tdom.py#render`.

### 3. Categories

Migrate:

- `docs/examples/categories/imperative_categories.md`;
- `docs/examples/categories/organizing_with_categories.md`.

Both pages share `examples/categories/categories_example.py`. Snippet ids should
be shared where the prose points at the same source section.

### 4. Hopscotch

Finish the pilot page and migrate:

- `docs/examples/hopscotch/resource.md`;
- `docs/examples/hopscotch/basic_container.md`;
- `docs/examples/hopscotch/app_site.md`;
- `docs/examples/hopscotch/override.md`;
- `docs/examples/hopscotch/location.md`;
- `docs/examples/hopscotch/scan_decorators.md`.

Each directory example should get an `example.toml` manifest. The current
`hopscotch-resource` manifest is the local pattern.

### 5. Middleware

Migrate:

- `docs/examples/middleware/aria.md`.

This is a multi-file bundle and should get an `example.toml` manifest. Snippets
should preserve the current teaching order: service, middleware, component, app,
then full source.

## Data Flow

During a docs build:

1. `tainie_tools.examples.sphinx` scans `tainie_examples_dir`.
2. It reads `example.toml` manifests and single-file examples.
3. `example-snippet` directives resolve named source markers.
4. `example-source` renders full source files.
5. The extension writes `example-inventory.json`.

This migration should not make Tainie import producer docs or example modules.
The inventory remains passive evidence emitted by the producer package docs
build.

## Error Handling

Sphinx should fail on:

- missing snippet ids;
- unknown example ids;
- `example-source` files outside a bundle;
- invalid manifests;
- invalid domain metadata.

Implementation should use those failures as the safety net rather than keeping
manual string anchors.

## Testing

Run after each grouped pass:

```bash
uv run pytest tests/test_examples.py -q
uv run sphinx-build -W -b html docs docs/_build/html
```

Final verification:

```bash
uv run pytest tests/test_examples.py -q
uv run sphinx-build -W -b html docs docs/_build/html
rg ":start-at:|:end-at:" docs/examples
test -f docs/_build/html/example-inventory.json
```

Expected final state:

- example tests pass;
- Sphinx builds with `-W`;
- `example-inventory.json` exists;
- no `:start-at:` or `:end-at:` anchors remain in `docs/examples`;
- no `literalinclude` usage remains in `docs/examples/**`.

## Roadmap Completion

After verification passes, mark roadmap item 48 `Complete Example Bundle
Migration` complete with a short completion note that names:

- all migrated example groups;
- generated example inventory;
- no remaining brittle anchors;
- verification commands.
