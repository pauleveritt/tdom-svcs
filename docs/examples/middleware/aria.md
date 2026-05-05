# Aria Verifier

This example demonstrates per-target middleware that validates accessibility by checking for missing `alt` attributes on images.

```{note}
This example uses Hopscotch patterns (`@hookable`, `@injectable`, `scan()`) for convenience.
You can also use imperative registration if preferred.
```

## Project structure

```
aria/
├── app.py              # Main entry point
├── components.py       # ImageWithAlt, ImageWithoutAlt with @hookable
├── middleware.py       # AriaVerifierMiddleware with Inject[Logger]
└── services.py         # Logger service
```

## The accessibility use case

Accessibility validation is a common cross-cutting concern. Rather than checking each component manually, middleware can inspect rendered output and collect warnings centrally.

The middleware renders each component, inspects the HTML output for `<img>`
elements missing `alt` attributes, and logs warnings via an injected Logger
service.

```{note}
This example demonstrates the pattern with a single check (missing alt on images). A production implementation would include a full tree walker checking for multiple ARIA violations: missing labels, invalid roles, keyboard accessibility issues, and more.
```

## Rendered output helps middleware

This middleware works with any tdom-svcs component that returns a template or
rendered HTML string. A broader Node standard could make richer tree inspection
possible later, but this example keeps the current implementation concrete and
boring.

## The Logger service

First, we define a simple logging service that collects warnings:

```{literalinclude} ../../../examples/middleware/aria/services.py
:start-at: @injectable
```

## Defining the verifier middleware

The `AriaVerifierMiddleware` uses `@injectable` (not `@middleware`) because it's attached to specific targets via `@hookable`, not registered globally:

```{literalinclude} ../../../examples/middleware/aria/middleware.py
:start-after: The aria verifier middleware
:end-at: return props
```

The middleware injects the `Logger` service and uses it to log warnings. It
renders the component, then parses the rendered HTML to find all `<img>`
elements.

### Inspecting the rendered HTML

The `_check_images` method uses a tiny `HTMLParser` helper:

```{literalinclude} ../../../examples/middleware/aria/middleware.py
:start-at: def _check_images
:end-at: self.logger.warn
```

## Components with per-target middleware

Components use the `@hookable` decorator to attach the middleware for the `rendering` phase:

```{literalinclude} ../../../examples/middleware/aria/components.py
:start-after: ImageWithAlt component with per-target middleware
:end-at: class ImageWithAlt:
```

A component with proper accessibility:

```{literalinclude} ../../../examples/middleware/aria/components.py
:lines: 18-22
```

A component missing the `alt` attribute:

```{literalinclude} ../../../examples/middleware/aria/components.py
:lines: 25-30
```

The middleware detects the missing `alt` by inspecting rendered HTML, with no
markers or special annotations needed.

## Verifying warnings

The app uses `execute_target_middleware` to run the per-target middleware and verifies warnings via the Logger:

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
