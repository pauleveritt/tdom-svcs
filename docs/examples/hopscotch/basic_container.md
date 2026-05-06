# Hopscotch Containers

In our examples so far, we've had to wire some things together manually. The Hopscotch family -- `HopscotchContainer`,
`HopscotchRegistry`, and `Inject` -- are designed to make dependency injection easier and more intuitive.

Let's switch the [inject service](../basic/inject_service) example to use Hopscotch.

## Registry and container

The most notable first point: we use `HopscotchRegistry` instead of `svcs.Registry`. This gives some helper functions
that you'll see in a moment, as well as using `HopscotchInjector` instead of `DefaultInjector`.

```{example-snippet} hopscotch/basic_container.py#registry-setup
```

Similarly, our context manager is `HopscotchContainer` instead of `svcs.Container`:

```{example-snippet} hopscotch/basic_container.py#container-context
```

The big surprise -- no more `registry.register_factory()` calls! Instead, we "scan" for "injectables":

```{example-snippet} hopscotch/basic_container.py#scan-call
```

In this case we are scanning in `locals` as this is a single file application. In larger systems, you would import
`components` and scan there. The `scan` function has lots of flexibility and can take a list of modules and package
strings.

## Injectables

How do we tell the registry that something should be registered? An `@injectable` decorator:

```{example-snippet} hopscotch/basic_container.py#database-service
```

The `Users` service depends on `Database` and reads the current request:

```{example-snippet} hopscotch/basic_container.py#users-service
```

The `Greeting` component injects `Users` and renders the current user:

```{example-snippet} hopscotch/basic_container.py#greeting-component
```

The `scan()` function from `svcs-di` registers the injectable services in the `registry`.

## Full source code

```{example-source} hopscotch/basic_container
```
