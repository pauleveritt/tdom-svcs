# Roadmap Standards

Use these standards when adding or reshaping entries in
`docs/superpowers/roadmap.md`. The roadmap is planning source material, not just
a backlog, so entries should preserve the reasoning needed by the next agent or
maintainer.

## Entry Shape

Each roadmap item should include:

- A priority marker (`P0`, `P1`, or `P2`) that reflects sequencing pressure.
- A concise title that names the outcome, not only the activity.
- Enough context to explain why the item exists and what it must not do.
- Acceptance criteria that can be reviewed later.
- A size marker (`S`, `M`, or `L`) for planning.

Prefer end-to-end, reviewable units. Split work when acceptance would otherwise
mix unrelated decisions, implementation, docs, and validation.

## Phase Shape

Each phase should start with a short narrative that explains:

- What changes after the phase is complete.
- Which earlier or external work it depends on.
- Which tempting local decisions are intentionally deferred.
- Why this package is the right place to prove the next step.

The narrative should make the order of items feel inevitable. If a later item
depends on another package, policy, or upstream API, say so directly instead of
burying the dependency in acceptance text.

## Dependency Handling

Use explicit waiting items when the responsible decision belongs elsewhere. A
blocked item is better than a local convention that will be wrong once the
upstream policy lands.

Good waiting items name:

- The upstream package or spec.
- The decision that must land there.
- The local constraint that must remain compatible with it.

Follow-on implementation items should not invent package-local formats,
validation rules, or source-of-truth conventions before the shared policy exists.

## Acceptance Criteria

Acceptance criteria should describe observable review outcomes:

- Tests, docs builds, or validation commands that must pass.
- Concrete files, symbols, examples, or concepts that must be covered.
- Compatibility promises, such as "no behavior changes" or "no custom glue."
- Deferrals that are part of the design, not omissions.

Avoid acceptance criteria that merely restate the task title.

## Advisory And Verified Facts

When roadmap work involves domain docs, evidence, or derived inventory, keep
prose and verified facts separate:

- Prose explains intent, sequencing, and authoring guidance.
- Verified facts should point to checkable symbols, package paths, examples, or
  tests whenever possible.
- Derived facts should remain derived; do not copy generated inventories into
  prose as if they were hand-authored truth.

If the shared authoring policy is not settled yet, write the roadmap item to
wait for that policy rather than encoding local rules prematurely.

## Notes Section

Keep the notes section short and architectural. It should summarize the purpose
of phases and link to durable research or standards when useful. Do not turn it
into a second backlog.
