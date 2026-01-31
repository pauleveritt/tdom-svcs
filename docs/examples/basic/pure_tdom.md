# `tdom` and the `context` argument

JSX and component-driven development have a well-known problem: prop-drilling. `tdom` solves this problem by providing a
`context` argument to all components.

## Analysis

Let's say we have some per-request data.

```{literalinclude} ../../../examples/basic/pure_tdom.py
:start-at: context =
:end-at: context =
```

We could supply this as a component argument, from parent to child, all the way down.
That kinda sucks. React calls this [prop drilling](https://react.dev/learn/passing-data-deeply-with-context).

Instead, we can add a keyword argument `context` to our `html()` call:

```{literalinclude} ../../../examples/basic/pure_tdom.py
:start-at: response =
:end-at: response =
```

This is a different `html()` function, imported from `tdom_svcs` instead of `tdom`. This function:

- Allows the extra dict-like `context` argument
- Forward it through the call chain
- Passes into components that with a parameter named `context`

That last part looks interesting. How does that work?

```{literalinclude} ../../../examples/basic/pure_tdom.py
:start-at: def Greeting
:end-at: return
```

The `Greeting` component now has a `context` argument. The component can pluck out whatever it needs.

This implementation is purely functional, using plain-old-argument-passing. No thread locals, no big magic.

## The `config` argument

The forked `tdom_svcs.html` also allows another keyword argument: `config`. This is a dict-like object with global setup
information. It's intended to be immutable and used only for internal `tdom` purposes. It would have a well-known
protocol "shape" defined by us, for the minimum expectations.

Two big examples:

- *Component location*. Given the name of a symbol, find the best implementation. Useful for letting sites replace
  built-in system components.
- *Component factory*. Change the way components are created and returned. Allows dependency injectors, middleware that
  runs before/after, etc.

It's probably that we'll just merge this with `context` so let's skip any examples.

## Full source code

```{literalinclude} ../../../examples/basic/pure_tdom.py
```
