# Hopscotch Examples

`svcs-di` has optional features under the name "Hopscotch" that make it easier to use `tdom` with `svcs`, while providing powerful features like automatic scanning, component overrides, and context-aware resolution.

## Basic container

Let's rewrite the [inject service](../basic/inject_service) example using a `HopscotchContainer` instead of `svcs.Container`. We use `@injectable` to register services and `scan()` to discover them. [Read More](basic_container)

## App with site

Follow the common pattern of a common app used in a particular site. The app provides components and services, while the site configures them. [Read More](app_site)

## Site overrides component

The site wants the same `Greeting` props/postinit, but a different template -- without forking. This example shows how a site can replace a component using `register_implementation()`. [Read More](override)

## Scanning for decorators

Instead of manually calling `register_implementation()`, use the `@injectable(for_=...)` decorator and let `scan()` discover overrides automatically. [Read More](scan_decorators)

## Resource variation

A site can conditionally override based on resource information. Use `Resource[T]` for injection and `@injectable(resource=...)` for conditional overrides. [Read More](resource)

## Location variation

A site can conditionally override based on URL location (e.g., `/fr/` for French). Pass a `location` parameter to the container and use `@injectable(location=...)` for path-based overrides. [Read More](location)

```{toctree}
:hidden:
:maxdepth: 1

basic_container
app_site
override
scan_decorators
resource
location
```
