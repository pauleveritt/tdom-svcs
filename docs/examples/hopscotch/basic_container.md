# Hopscotch Containers

In our examples so far, we've had to wire some things together manually. The Hopscotch family -- `HopscotchContainer`,
`HopscotchRegistry`, and `Inject` -- are designed to make dependency injection easier and more intuitive.

Let's switch the [inject service](../basic/inject_service) example to use Hopscotch.

## Registry and container

The most notable first point: we use `HopscotchRegistry` instead of `svcs.Registry`. This gives some helper functions
that you'll see in a moment, as well as using `HopscotchInject` instead of `DefaultInject`.

```{literalinclude} ../../../examples/hopscotch/basic_container.py
:start-at: registry = HopscotchRegistry
:end-at: registry = HopscotchRegistry
```

Similarly, our context manager is `HopscotchContainer` instead of `svcs.Container`:

```{literalinclude} ../../../examples/hopscotch/basic_container.py
:start-at: with HopscotchContainer
:end-at: with HopscotchContainer
```

The big surprise -- no more `registry.register_factory()` calls! Instead, we "scan" for "injectables":

```{literalinclude} ../../../examples/hopscotch/basic_container.py
:start-at: Auto-discover
:end-at: scan(
```

In this case we are scanning in `locals` as this is a singl file application. In larger systems, you would import
`components` and scan there. The `scan` function has lots of flexibility and can take a list of modules and package
strings.

## Injectables

How do we tell the registry that something should be registered? An `@injectable` decorator:

```{literalinclude} ../../../examples/hopscotch/basic_container.py
:start-after: The underlying service
:end-at: class Database
```

The `scan()` function from `svcs-di` does its magic and registers the `Database` service in the `registry`.

## Full source code

```{literalinclude} ../../../examples/hopscotch/basic_container.py
```
