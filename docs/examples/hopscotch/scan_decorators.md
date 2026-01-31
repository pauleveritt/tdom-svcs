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

```{literalinclude} ../../../examples/common/components.py
:start-at: @dataclass
:end-at: Hello
```

## The site's override with `for_=`

The site defines `FrenchGreeting` with `@injectable(for_=Greeting)`:

```{literalinclude} ../../../examples/hopscotch/scan_decorators/site/components.py
:start-at: @injectable
:end-at: Bonjour
```

The `for_=Greeting` parameter tells the scanner that this class is an implementation of `Greeting`.
When scanned, it automatically calls `registry.register_implementation(Greeting, FrenchGreeting)`.

## Site setup scans for overrides

The site's `svcs_registry()` function is called automatically during `scan()`:

```{literalinclude} ../../../examples/hopscotch/scan_decorators/site/__init__.py
```

## The app wires it together

The `app.py` first scans the base app modules, then scans the site (which automatically calls `svcs_registry()`):

```{literalinclude} ../../../examples/hopscotch/scan_decorators/app.py
:start-at: def main
:end-at: scan(registry, components, services, site)
```

The site's scan happens after the app's scan, so the override takes precedence.

## Full source code

### app.py

```{literalinclude} ../../../examples/hopscotch/scan_decorators/app.py
```

### components.py

```{literalinclude} ../../../examples/hopscotch/scan_decorators/components.py
```

### site/\_\_init\_\_.py

```{literalinclude} ../../../examples/hopscotch/scan_decorators/site/__init__.py
```

### site/components.py

```{literalinclude} ../../../examples/hopscotch/scan_decorators/site/components.py
```
