# Basic tdom with svcs

This `tdom` fork is largely about components so let's focus our examples there. While these are implemented with `svcs` containers, many ideas could work with anything dict-like.

## Overview

This example demonstrates:
- Passing an `svcs.Container` to `html()` as context
- Automatic injection of `Inject[]` parameters into components
- Service dependencies with `auto()`

## The Database Service

We start with a simple database service that stores users:

```{literalinclude} ../../../examples/basic/tdom_svcs.py
:start-at: @dataclass
:end-at: return list(self._users.values())
```

## A Service with Dependencies

The `Service` class demonstrates injecting one service into another:

```{literalinclude} ../../../examples/basic/tdom_svcs.py
:start-after: def list_users
:end-at: timeout: int = 30
```

## The Greeting Component

A function component that receives the injected `Service`:

```{literalinclude} ../../../examples/basic/tdom_svcs.py
:start-at: def Greeting
:end-at: return html
```

## Wiring It Together

The `main()` function sets up the registry and renders the component:

```{literalinclude} ../../../examples/basic/tdom_svcs.py
:start-at: def main
:end-at: return result
```

## Full Source Code

```{literalinclude} ../../../examples/basic/tdom_svcs.py
```
