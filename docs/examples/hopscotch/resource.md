# Resource-Based Variation

Sometimes you want different component implementations based on the type of "resource" being processed.
For example, a French customer might see a French greeting, while a default customer sees an English one.

This example shows how to use `Resource[T]` for injection and `@injectable(resource=...)` for
conditional overrides.

## The concept

- The container is created with a `resource` parameter
- Components use `Resource[T]` to inject the current resource
- Overrides can be registered for specific resource types using `@injectable(for_=..., resource=...)`

## Defining resources

The base app defines a `Customer` protocol and a `DefaultCustomer`:

```{literalinclude} ../../../examples/hopscotch/resource/resources.py
```

The site adds a `FrenchCustomer`:

```{literalinclude} ../../../examples/hopscotch/resource/site/resources.py
```

## Injecting resources with `Resource[T]`

The `Greeting` component uses `Resource[DefaultCustomer]` to inject the current resource:

```{literalinclude} ../../../examples/hopscotch/resource/components.py
:start-at: @dataclass
:end-at: Hello
```

The `Resource[T]` annotation tells the injector to grab the resource from the container
and provide it with type `T`.

## Resource-based override

The site defines `FrenchGreeting` with `@injectable(for_=Greeting, resource=FrenchCustomer)`:

```{literalinclude} ../../../examples/hopscotch/resource/site/components.py
:start-at: @injectable
:end-at: Bonjour
```

This override only applies when the container's resource is a `FrenchCustomer`.

## Passing resources to the container

The app creates containers with different resources:

```{literalinclude} ../../../examples/hopscotch/resource/app.py
:start-at: First request
:end-at: results.append
```

For the French customer:

```{literalinclude} ../../../examples/hopscotch/resource/app.py
:start-at: Second request
:end-at: results.append
```

When the resource is `DefaultCustomer`, the base `Greeting` is used.
When the resource is `FrenchCustomer`, the `FrenchGreeting` override is selected.

## Full source code

### app.py

```{literalinclude} ../../../examples/hopscotch/resource/app.py
```

### components.py

```{literalinclude} ../../../examples/hopscotch/resource/components.py
```

### resources.py

```{literalinclude} ../../../examples/hopscotch/resource/resources.py
```

### site/components.py

```{literalinclude} ../../../examples/hopscotch/resource/site/components.py
```

### site/resources.py

```{literalinclude} ../../../examples/hopscotch/resource/site/resources.py
```
