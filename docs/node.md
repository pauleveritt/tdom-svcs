# The Node Standard

A common interface for Python web ecosystem interoperability.

## The Fragmentation Problem

Python's web templating ecosystem is fragmented. Jinja2, Mako, Django templates, and others each produce strings
directly. This makes it difficult to:

- **Test templates** without parsing HTML strings
- **Compose tools** that work across different templating libraries
- **Build pipelines** for static site generation or server-side rendering
- **Create accessibility tools** that analyze component output

When templates produce strings, every tool in the chain must parse HTML to understand the structure. This is slow,
error-prone, and loses semantic information.

## The Node Type

The `Node` type from [tdom](https://github.com/pauleveritt/tdom) provides a standard intermediate representation:

```python
@dataclass
class Node:
    tag: str  # Element name: "div", "button", etc.
    attrs: dict[str, str | bool]  # Attributes: {"class": "btn", "disabled": True}
    children: tuple[Node | str, ...]  # Child nodes or text content
```

Instead of producing HTML strings directly, templates produce `Node` trees. The final rendering to HTML happens at the
end of the pipeline.

## Node in Action

Because Node is a data structure (not a string), tools can inspect and act on it directly.

**Testing with aria-testing** - Query by role, just like Testing Library:

```python
from aria_testing import query_all_by_tag_name

images = query_all_by_tag_name(node, "img")
for img in images:
    if "alt" not in img.attrs:
        logger.warn("img missing alt attribute")
```

**Asset collection** - Walk the tree to find static assets:

```python
match node:
    case Element(tag="link", attrs=attrs):
        collector.register_asset(attrs.get("href"))
    case Element(tag="script", attrs=attrs):
        collector.register_asset(attrs.get("src"))
```

**ARIA validation** - Check accessibility before rendering:

```python
def validate(node: Node) -> None:
    for img in query_all_by_tag_name(node, "img"):
        assert "alt" in img.attrs, "Images must have alt text"
```

See the {doc}`examples/middleware/aria` and {doc}`examples/middleware/path` examples for complete implementations.

## The Ecosystem Vision

A standard Node type enables a rich ecosystem of interoperable tools. When everything speaks the same language,
components, middleware, and tooling can be mixed and matched freely.

### Core Layer

The foundation that everything builds on:

- **Node type** - The standard intermediate representation
- **Template function** - Convert PEP 750 t-strings to Node trees
- **Context passing** - Share state across the component tree
- **Dependency injection** - Inject services into components
- **Layouts** - Reusable page structures and structural components

### Component-Driven Development

Build UIs from isolated, reusable components:

- **aria-testing** - Query components by ARIA role and accessible name, just like Testing Library
- **Storyville** - Component catalog for development, documentation, and sharing
- **Theme libraries** - Pre-built component sets that work with any Node-based project

### Middleware Pipeline

Cross-cutting concerns handled declaratively:

- **Validation** - ARIA compliance checking, HTML validation
- **Link checking** - Detect broken internal and external links
- **Asset processing** - Responsive image generation, static file rewriting
- **Logging** - Request tracing, performance monitoring
- **Listings** - Automatic collection of pages, posts, or other content

See the middleware examples:

- {doc}`examples/middleware/basic_middleware` - Chain execution, priority, and logging
- {doc}`examples/middleware/aria` - ARIA validation that collects accessibility warnings
- {doc}`examples/middleware/path` - Asset path collection during render

### Framework Integration

Bring Node-based components to existing frameworks:

- **tdom-django** - Use Node components in Django templates
- **htpy interop** - Share components between tdom and htpy ecosystems
- **SSG integration** - Static site generators that process Node trees

### Developer Experience

Tooling that understands your components:

- **Linting** - Catch accessibility issues, validate props
- **IDE support** - Autocomplete for component props and children, navigation
- **Type checking** - Static analysis of component props and children
- **Testing** - Query components by role
- **Storybook integration** - Visualize component trees in Storybook

## How It Works Together

Consider a typical page render:

1. **Request arrives** - Framework passes request context
2. **Components resolve** - Dependencies injected, overrides applied
3. **Middleware runs** - Validation, logging, asset collection
4. **Node tree built** - Components return Nodes, not strings
5. **Post-processing** - Link checking, image optimization on the tree
6. **Final render** - Convert Node tree to HTML string once, at the end

Because every step works with Nodes, tools compose naturally. A component library works with any middleware. A linter
works with any framework. An asset processor works with any theme.

## Current Status

Available now:

- **Node type and templating** - Core foundation
- **Context and middleware** - Cross-cutting concerns
- **aria-testing** - Testing Library-style queries

Coming soon:

- **Layouts** - Reusable page structures
- **Themester** - Portable view/theme layer across frameworks
- **Storyville** - Component development environment

The ecosystem is young, but the foundation is solid. Build on Node and your work interoperates with everything else.

## Learn More

- [tdom](https://github.com/pauleveritt/tdom) - The Node type implementation
- {doc}`core_concepts` - Components, context, and dependency injection
- {doc}`examples/index` - Working examples
