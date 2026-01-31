# Basic Examples

These examples cover the foundational concepts of `tdom-svcs`: the `context` argument, component flavors, and dependency injection basics.

## tdom and the context argument

JSX and component-driven development have a well-known problem: prop-drilling. `tdom` solves this problem by providing a `context` keyword argument to the `html()` function, passed down to the call chain. [Read More](pure_tdom)

## Basic tdom with svcs

This `tdom` fork is largely about components so let's focus our examples there. While these are implemented with `svcs` containers, many ideas could work with anything dict-like. [Read More](tdom_svcs)

## Functions, dataclasses, and POCOs

Want `context` but in a dataclass component? How about a plain old class object (POCO)? Let's see that, along with how `__post_init__` can help. [Read More](function_dataclass_poco)

## Inject in a service

Want to inject a service into another service? Let's see how that works, using the `DefaultInjector` in `svcs-di`. [Read More](inject_service)

## Props priority

How can our component clearly project exactly what it needs, minimum surface area, and allow a prop override? Let's use dataclass `InitVar` and `__post_init__` to calculate exactly what the template needs. [Read More](props_priority)

```{toctree}
:hidden:
:maxdepth: 1

pure_tdom
tdom_svcs
function_dataclass_poco
inject_service
props_priority
```
