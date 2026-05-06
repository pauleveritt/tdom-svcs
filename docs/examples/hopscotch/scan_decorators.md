# Scanning for Decorators

Instead of manually calling `register_implementation()`, you can use the `@injectable(for_=...)` decorator
and let `scan()` discover overrides automatically. This example restructures the app/site layout to use
decorator-based registration.

## Project structure

```
scan_decorators/
├── app.py              # Main entry point
├── components.py       # Base Greeting component
├── services.py         # Database, Users services
├── request.py          # Request dataclass
└── site/
    ├── __init__.py     # svcs_registry() that scans site components
    └── components.py   # FrenchGreeting with @injectable(for_=Greeting)
```

## The base component

The `Greeting` component is defined in `examples/common/components.py` and re-exported:

```{example-snippet} common/components.py#greeting-component
```

## The site's override with `for_=`

The site defines `FrenchGreeting` with `@injectable(for_=Greeting)`:

```{example-snippet} hopscotch-scan-decorators:site/components.py#decorated-override
```

The `for_=Greeting` parameter tells the scanner that this class is an implementation of `Greeting`.
When scanned, it automatically calls `registry.register_implementation(Greeting, FrenchGreeting)`.

## Site setup scans for overrides

The site's `svcs_registry()` function is called automatically during `scan()`:

```{example-snippet} hopscotch-scan-decorators:site/__init__.py#site-registry
```

## The app wires it together

The `app.py` first scans the base app modules, then scans the site (which automatically calls `svcs_registry()`):

```{example-snippet} hopscotch-scan-decorators:app.py#scan-app-site
```

The site's scan happens after the app's scan, so the override takes precedence.

## Full source code

```{example-source} hopscotch-scan-decorators
:files: app.py, components.py, request.py, services.py, site/__init__.py, site/components.py
```
