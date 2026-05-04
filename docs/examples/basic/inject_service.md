# Inject Service

We saw using `Inject[]` on component parameters. This works because our `tdom_svcs.html` "fork" looks for this marker
and does the injection.

That works for *components*. What about *services*? In this example, we'll look at using the new `auto()` wrapper in
`svcs-di`.

## The `Users` needs the `Database`

Our `Users` service needs the database, so it injects the `Database` service:

```{literalinclude} ../../../examples/basic/inject_service.py
:lines: 22-43
```

Notice `get_current_user`? How does `Users` know what is "current"? The container knows! It has the `Request`.

Our container now has a `Users` service that grabs the `Database` and `Request` services. These are all set up,
our way, ready for use.

## Component grabs service

For example, by a `Greeting` component:

```{literalinclude} ../../../examples/basic/inject_service.py
:lines: 46-55
```

This is a nice use of injection. Instead of grabbing the entire context, we make it clear, right on the dataclass
fields, *which* data we need from the context container (or passed in via prop.)

You could even be more explicit and use `__post_init__` to narrow the surface area down to `user_id`. Even further: same
place, grab the username, leaving the template rendering function with no logic.

## Setup

With these three services and one component in place, time to wire things up:

```{literalinclude} ../../../examples/basic/inject_service.py
:lines: 58-64
```

Here we see the use of `auto()`, as `Users` injects a dependency from `Database`.

Then a request comes in, so we put it in the container:

```{literalinclude} ../../../examples/basic/inject_service.py
:lines: 66-70
```

Our `html()` call passes in the container as the "context" value:

```{literalinclude} ../../../examples/basic/inject_service.py
:lines: 72-75
```

Our modified `tdom_svcs.html()` function checks for any injection and passes in the `Users` service.

## Full source code

```{literalinclude} ../../../examples/basic/inject_service.py
```
