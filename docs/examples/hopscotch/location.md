# Hopscotch Location Variation

- Vary the `Greeting` based on URL location
- Base app uses default greeting for most paths
- Site overrides with `FrenchGreeting` for paths starting with `/fr`

## Location-based resolution

When creating a `HopscotchContainer`, you can pass a `location` parameter with a `PurePath`:

```{example-snippet} hopscotch-location:app.py#default-request
```

For French URLs, we pass a different location:

```{example-snippet} hopscotch-location:app.py#french-request
```

## Registering location-based overrides

The site registers `FrenchGreeting` to override `Greeting` when the location starts with `/fr`:

```{example-snippet} hopscotch-location:site/components.py#french-greeting
```

The `location=PurePath("/fr")` parameter tells the registry that this implementation should be used when the container's location starts with `/fr`.

## Base component

The base `Greeting` component injects the `Users` service:

```{example-snippet} hopscotch-location:components.py#base-greeting
```

## Full source code

```{example-source} hopscotch-location
:files: app.py, components.py, request.py, services.py, site/__init__.py, site/components.py
```
