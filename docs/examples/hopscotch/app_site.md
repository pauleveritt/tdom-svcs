# App with Site

Real applications often have a common "app" codebase that is customized by different "sites." This pattern separates
reusable components and services from site-specific configuration.

This example shows the app/site pattern: the app provides components and services, while the site configures them.

## Project structure

The example is split across multiple files:

- `app_common.py` - Shared services (`Database`, `Users`) and components (`Greeting`)
- `site.py` - Site-specific configuration via `svcs_registry()`
- `app.py` - Main entry point that wires everything together

## The app entry point

The `app.py` file sets up the registry, scans for injectables, then scans the site (which automatically calls `svcs_registry()`):

```{example-snippet} hopscotch-app-site:app.py#app-scan
```

Note how we scan both `app_common` (which registers all `@injectable` classes) and `site` in a single call.

## Shared components

The `app_common.py` file contains services and components that any site can use:

```{example-snippet} hopscotch-app-site:app_common.py#base-component
```

The `Greeting` component uses `Inject[Users]` to get the current user from the database.

## Site configuration

The `site.py` file provides a `svcs_registry()` function that is called automatically during `scan()`:

```{example-snippet} hopscotch-app-site:site.py#site-registry
```

In this simple example, the site doesn't make any changes. But this is where a site would register
overrides, additional services, or custom implementations.

## Using the container

Back in `app.py`, we create a container and render the component:

```{example-snippet} hopscotch-app-site:app.py#render-component
```

The `Request` is registered as a local value (per-request data), then the `Greeting` component
is rendered with the container as context.

## Full source code

```{example-source} hopscotch-app-site
:files: app.py, app_common.py, site.py
```
