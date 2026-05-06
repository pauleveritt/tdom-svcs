# Resource-Based Variation

Sometimes you want different component implementations based on the type of "resource" being processed.
For example, a French customer might see a French greeting, while a default customer sees an English one.

This example shows how to use `Resource[T]` for injection and `@injectable(resource=...)` for
conditional overrides.

## The concept

- The container is created with a `resource` parameter
- Components use `Resource[T]` to inject the current resource
- Overrides can be registered for specific resource types using `@injectable(for_=..., resource=...)`

:::{domain:concept} Resource resolution
:id: resource-resolution
:status: verified
:kind: selection
:ref: svcs_hopscotch:Resource

Component fields can request the active Hopscotch resource with `Resource[T]`,
and component registrations can use the active resource type during selection.
:::

:::{domain:rule} Resource-specific override
:id: resource-specific-override
:status: verified
:applies-to: resource-resolution

When a site registers an implementation for a specific resource type, that
implementation is selected only for containers carrying a matching resource.
:::

## Defining resources

The base app defines a `Customer` protocol and a `DefaultCustomer`:

```{example-snippet} hopscotch-resource:resources.py#default-resource
```

The site adds a `FrenchCustomer`:

```{example-snippet} hopscotch-resource:site/resources.py#french-resource
```

## Injecting resources with `Resource[T]`

The `Greeting` component uses `Resource[DefaultCustomer]` to inject the current resource:

```{example-snippet} hopscotch-resource:components.py#resource-greeting
```

The `Resource[T]` annotation tells the injector to grab the resource from the container
and provide it with type `T`.

## Resource-based override

The site defines `FrenchGreeting` with `@injectable(for_=Greeting, resource=FrenchCustomer)`:

```{example-snippet} hopscotch-resource:site/components.py#french-greeting
```

This override only applies when the container's resource is a `FrenchCustomer`.

## Passing resources to the container

The app creates containers with different resources:

```{example-snippet} hopscotch-resource:app.py#default-request
```

For the French customer:

```{example-snippet} hopscotch-resource:app.py#french-request
```

When the resource is `DefaultCustomer`, the base `Greeting` is used.
When the resource is `FrenchCustomer`, the `FrenchGreeting` override is selected.

## Full source code

```{example-source} hopscotch-resource
:files: app.py, components.py, resources.py, site/components.py, site/resources.py
```
