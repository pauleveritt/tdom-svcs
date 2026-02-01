# Aria Verifier

This example demonstrates per-component middleware that validates accessibility by checking for missing `alt` attributes on images.

```{note}
This example uses Hopscotch patterns (`@component`, `@injectable`, `scan()`) for convenience.
You can also use imperative registration if preferred.
```

## Project structure

```
aria/
├── app.py              # Main entry point
├── components.py       # ImageWithAlt, ImageWithoutAlt with @component
├── middleware.py       # AriaVerifierMiddleware with Inject[Logger]
└── services.py         # Logger service
```

## The accessibility use case

Accessibility validation is a common cross-cutting concern. Rather than checking each component manually, middleware can inspect rendered output and collect warnings centrally.

This example uses [aria-testing](https://github.com/pauleveritt/aria-testing) to query the Node tree for `<img>` elements missing `alt` attributes. The middleware renders each component, inspects the output, and logs warnings via an injected Logger service.

```{note}
This example demonstrates the pattern with a single check (missing alt on images). A production implementation would include a full tree walker checking for multiple ARIA violations: missing labels, invalid roles, keyboard accessibility issues, and more.
```

## Node standards help middleware

This middleware will work in any tdom site on any component that returns a `tdom.Node`. That's great and real value for a broad ecosystem of tdom components and middleware.

But why limit this to tdom? What if the entire Python ecosystem could agree on some interoperability standards, such as a common Node interface? Like with WSGI middleware, such standards could help Python pool together its web story, instead of fragmenting.

## The Logger service

First, we define a simple logging service that collects warnings:

```{literalinclude} ../../../examples/middleware/aria/services.py
:start-at: @injectable
```

## Defining the verifier middleware

The `AriaVerifierMiddleware` uses `@injectable` (not `@middleware`) because it's attached to specific components via `@component`, not registered globally:

```{literalinclude} ../../../examples/middleware/aria/middleware.py
:start-after: The aria verifier middleware
:end-at: return props
```

The middleware injects the `Logger` service and uses it to log warnings. It renders the component, then uses `query_all_by_tag_name` from aria-testing to find all `<img>` elements.

### Inspecting the Node tree

The `_check_images` method uses aria-testing's query functions:

```{literalinclude} ../../../examples/middleware/aria/middleware.py
:start-at: def _check_images
:end-at: self.logger.warn
```

## Components with per-component middleware

Components use the `@component` decorator to attach the middleware for the `rendering` phase:

```{literalinclude} ../../../examples/middleware/aria/components.py
:start-after: ImageWithAlt component with per-component middleware
:end-at: class ImageWithAlt:
```

A component with proper accessibility:

```{literalinclude} ../../../examples/middleware/aria/components.py
:start-at: class ImageWithAlt:
:end-at: return html
```

A component missing the `alt` attribute:

```{literalinclude} ../../../examples/middleware/aria/components.py
:start-at: class ImageWithoutAlt:
:end-at: return html
```

The middleware detects the missing `alt` by inspecting the rendered Node tree—no markers or special annotations needed.

## Verifying warnings

The app uses `execute_component_middleware` to run the per-component middleware and verifies warnings via the Logger:

```{literalinclude} ../../../examples/middleware/aria/app.py
:start-at: logger = container.get(Logger)
:end-at: assert "missing alt"
```

## Running the example

```bash
uv run python -m examples.middleware.aria.app
```

Output:

```
<div><img src="photo.jpg" alt="A photo"></div>
```

The example uses assertions to verify that warnings are collected. The final render shows the accessible component.

## Full source code

### `app.py`

```{literalinclude} ../../../examples/middleware/aria/app.py
```

### `middleware.py`

```{literalinclude} ../../../examples/middleware/aria/middleware.py
```

### `components.py`

```{literalinclude} ../../../examples/middleware/aria/components.py
```

### `services.py`

```{literalinclude} ../../../examples/middleware/aria/services.py
```
