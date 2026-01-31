# Hopscotch Location Variation

- Vary the `Greeting` based on URL location
- Base app uses default greeting for most paths
- Site overrides with `FrenchGreeting` for paths starting with `/fr`

## Location-based resolution

When creating a `HopscotchContainer`, you can pass a `location` parameter with a `PurePath`:

```{literalinclude} ../../../examples/hopscotch/location/app.py
:start-at: First request
:end-at: results.append
```

For French URLs, we pass a different location:

```{literalinclude} ../../../examples/hopscotch/location/app.py
:start-at: Second request
:end-at: results.append
```

## Registering location-based overrides

The site registers `FrenchGreeting` to override `Greeting` when the location starts with `/fr`:

```{literalinclude} ../../../examples/hopscotch/location/site/components.py
:start-at: @injectable
:end-at: Bonjour
```

The `location=PurePath("/fr")` parameter tells the registry that this implementation should be used when the container's location starts with `/fr`.

## Base component

The base `Greeting` component injects the `Users` service:

```{literalinclude} ../../../examples/hopscotch/location/components.py
:start-at: @dataclass
:end-at: Hello
```

## Full source code

### app.py

```{literalinclude} ../../../examples/hopscotch/location/app.py
```

### components.py

```{literalinclude} ../../../examples/hopscotch/location/components.py
```

### site/components.py

```{literalinclude} ../../../examples/hopscotch/location/site/components.py
```
