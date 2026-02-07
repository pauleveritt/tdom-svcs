# Basic Injection with svcs.Container

This example demonstrates the foundation of dependency injection in tdom-svcs using the standard `svcs.Container`.

## Overview

This example demonstrates:
- Passing an `svcs.Container` to `html()` as context
- Automatic injection of `Inject[]` parameters into components
- Service dependencies with `auto()`
- Function components with injected services

## The Database Service

We start with a simple database service that stores users:

```{literalinclude} ../../../examples/basic/svcs_container.py
:start-at: @dataclass
:end-at: return list(self._users.values())
```

## A Service with Dependencies

The `Service` class demonstrates injecting one service into another:

```{literalinclude} ../../../examples/basic/svcs_container.py
:start-after: def list_users
:end-at: timeout: int = 30
```

Notice the `Inject[Database]` annotation - this tells the container to inject the `Database` service.

## The Greeting Component

A function component that receives the injected `Service`:

```{literalinclude} ../../../examples/basic/svcs_container.py
:start-at: def Greeting
:end-at: return html
```

The `service: Inject[Service]` parameter is automatically resolved from the container.

## Wiring It Together

The `main()` function sets up the registry and renders the component:

```{literalinclude} ../../../examples/basic/svcs_container.py
:start-at: def main
:end-at: return result
```

Key points:
- We register `Database` with a simple factory
- We use `auto(Service)` because `Service` has injected dependencies
- We pass the container as the `context` parameter to `html()`
- The container automatically resolves all `Inject[]` parameters

## Full Source Code

```{literalinclude} ../../../examples/basic/svcs_container.py
```
