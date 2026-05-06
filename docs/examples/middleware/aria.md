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

```{example-snippet} middleware-aria:services.py#logger-service
```

## Defining the verifier middleware

The `AriaVerifierMiddleware` uses `@injectable` (not `@middleware`) because it's attached to specific targets via `@hookable`, not registered globally:

```{example-snippet} middleware-aria:middleware.py#middleware-class
```

The middleware injects the `Logger` service and uses it to log warnings. It
renders the component, then parses the rendered HTML to find all `<img>`
elements.

### Inspecting the rendered HTML

The `_check_images` method uses a tiny `HTMLParser` helper:

```{example-snippet} middleware-aria:middleware.py#image-check
```

## Components with per-target middleware

Components use the `@hookable` decorator to attach the middleware for the `rendering` phase:

```{example-snippet} middleware-aria:components.py#image-with-alt
```

A component missing the `alt` attribute:

```{example-snippet} middleware-aria:components.py#image-without-alt
```

The middleware detects the missing `alt` by inspecting rendered HTML, with no
markers or special annotations needed.

## Verifying warnings

The app uses `execute_target_middleware` to run the per-target middleware and verifies warnings via the Logger:

```{example-snippet} middleware-aria:app.py#registry-setup
```

```{example-snippet} middleware-aria:app.py#middleware-checks
```

```{example-snippet} middleware-aria:app.py#render-target
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

```{example-source} middleware-aria
:files: app.py, middleware.py, components.py, services.py
```
