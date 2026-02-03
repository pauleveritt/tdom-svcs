# Shape: Reorganize Docs

## Problem

The current documentation structure has several issues:

1. **README is too detailed** - Contains full sections on Key Concepts, Context/Config, Middleware, and Type Aliases that duplicate content in the docs/
2. **Empty placeholder** - `docs/examples/node/index.md` is a placeholder with no content
3. **Missing key content** - No documentation explaining the value of the Node type as a standard for Python web ecosystem interoperability

## Appetite

Small batch - a few hours of work to reorganize existing content and write one new page.

## Solution

### Slim README
The README should be a quick-start guide that gets developers up and running, then points them to the full docs for deeper content. Remove:
- Key Concepts section (decorators, class vs function components, container/registry, overrides, injector selection)
- Context and Config section
- Middleware section
- Type Aliases section

Keep:
- Installation
- Requirements
- Overview (shortened)
- Quick Start example
- Testing commands
- Clear links to documentation

### Delete Node Examples Placeholder
The `docs/examples/node/index.md` placeholder adds no value. Delete it and remove from the examples index. The aria-testing example is now covered in the middleware examples.

### Create Node Standard Page
Create `docs/node.md` explaining:
- The fragmentation problem in Python web templating
- How a standard Node type enables ecosystem interoperability
- What the Node interface provides (tag, attrs, children)
- Benefits for different use cases (templating, testing, SSG, rendering)
- How tdom and tdom-svcs leverage this standard

## Rabbit Holes

- Don't try to make the README a comprehensive guide - that's what docs/ is for
- Don't over-document the Node type - keep it focused on the "why" of standardization

## No-Gos

- Don't reorganize the entire docs structure - just these specific changes
- Don't create new example files - only documentation
