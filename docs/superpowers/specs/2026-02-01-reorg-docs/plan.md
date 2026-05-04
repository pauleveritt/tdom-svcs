# Reorganize Docs

## Summary

Reorganize documentation structure: slim down the README to essentials, delete the empty `examples/node` placeholder, and create a new top-level page about the value of a standard Node type for Python web ecosystem interoperability.

---

## Files to Modify

### README.md
**Action:** Slim down to essentials
- Keep: Brief intro, installation, requirements
- Keep: Simplified quick start example
- Remove: Detailed Key Concepts section (move to docs/)
- Remove: Detailed Context/Config section (already in docs/)
- Remove: Middleware section (already in docs/)
- Remove: Type Aliases section
- Add: Clear links to docs for deeper content

### docs/examples/node/index.md
**Action:** Delete
- Currently a placeholder with "Examples demonstrating Node ecosystem integration will be added here."
- Empty toctree

### docs/examples/index.md
**Action:** Remove Node Examples section
- Delete the "Node Examples" section and toctree entry
- Remove from TODO list reference to aria-testing (it's in the aria middleware example now)

### docs/index.md
**Action:** Add link to new Node page

### docs/node.md
**Action:** Create new page
- Title: "The Node Standard"
- Focus: Ecosystem interoperability value
- Content:
  - Why a standard Node type matters
  - What the Node type provides (tag, attrs, children)
  - Ecosystem benefits (templating, testing, SSG, rendering)
  - How different tools can interoperate
  - Link to tdom for implementation details

---

## Task Breakdown

### Task 1: Save Spec Documentation
Create `agent-os/specs/2026-02-01-reorg-docs/` with:
- `plan.md` — This plan
- `shape.md` — Shaping notes from conversation

### Task 2: Create docs/node.md
New page about Node type ecosystem value:
- Introduction to the problem (fragmented Python web ecosystem)
- The Node type as a common interface
- Benefits for different use cases
- How tdom-svcs leverages this

### Task 3: Slim Down README.md
- Reduce to: intro, installation, quick start, links to docs
- Remove detailed sections (Key Concepts, Context/Config, Middleware, Type Aliases)
- Add clear navigation to docs/ for full content

### Task 4: Delete Node Examples Placeholder
- Delete `docs/examples/node/index.md`
- Update `docs/examples/index.md` to remove Node section
- Clean up toctree

### Task 5: Update docs/index.md
- Add link to new `node.md` page in appropriate section

---

## Verification

1. `uv run sphinx-build -W docs docs/_build` — Docs build cleanly with no warnings
2. Review `docs/node.md` content is clear and valuable
3. Verify README is concise but complete for getting started
4. Check no broken links from removing node examples
