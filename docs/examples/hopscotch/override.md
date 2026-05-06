# Site Overrides Component

The app ships with builtin behavior, but a site wants to customize it -- without forking. This example shows how
a site can replace a component using `register_implementation()`.

## The problem

Your app has a `Greeting` component that says "Hello." A French site wants it to say "Bonjour" instead.
Rather than forking the entire app, the site can register its own implementation.

## The app's component

The base `Greeting` component lives in `app_common.py`:

```{example-snippet} hopscotch-override:app_common.py#base-component
```

## The site's override

The site defines `FrenchGreeting` that extends `Greeting`, keeping the same dependencies but changing the template:

```{example-snippet} hopscotch-override:site.py#override-component
```

Note that `FrenchGreeting` inherits from `Greeting`, so it gets the same `users: Inject[Users]` field.
Only the `__call__` method is overridden.

## Registering the override

The site's `svcs_registry()` function uses `register_implementation()` to tell the registry that
`FrenchGreeting` should be used whenever `Greeting` is requested:

```{example-snippet} hopscotch-override:site.py#register-override
```

## The app wires it together

The `app.py` scans the app modules first, then scans the site (which automatically calls `svcs_registry()`):

```{example-snippet} hopscotch-override:app.py#app-scan
```

Now when the template uses `<{Greeting} />`, the registry returns `FrenchGreeting` instead:

```{example-snippet} hopscotch-override:app.py#render-override
```

The assertions confirm that "Bonjour" appears and "Hello" does not.

## Full source code

```{example-source} hopscotch-override
:files: app.py, app_common.py, site.py
```
