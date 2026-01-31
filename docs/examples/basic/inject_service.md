# Inject Service

We saw using `Inject[]` on component parameters. This works because our `tdom_svcs.html` "fork" looks for this marker
and does the injection.

That works for *components*. What about *services*? In this example, we'll look at using the new `auto()` wrapper in
`svcs-di`.

## The `Users` needs the `Database`

We have an underlying `Database` service:

```{literalinclude} ../../../examples/basic/inject_service.py
:start-after: The underlying service
:end-at: self.users
```

Our `Users` service needs the database, so it injects the `Database` service:

```{literalinclude} ../../../examples/basic/inject_service.py
:start-at: A service that depends on the database
:end-at: return list(self.db.users.values())
```

Notice `get_current_user`? How does `Users` know what is "current"? The container knows! It has the `Request`.

Our container now has a `Users` service that grabs the `Database` and `Request` services. These are all set up,
our way, ready for use.

## Component grabs service

For example, by a `Greeting` component:

```{literalinclude} ../../../examples/basic/inject_service.py
:start-at: A component that injects the Users service
:end-at: return html(
```

This is a nice use of injection. Instead of grabbing the entire context, we make it clear, right on the dataclass
fields, *which* data we need from the context container (or passed in via prop.)

You could even be more explicit and use `__post_init__` to narrow the surface area down to `user_id`. Even further: same
place, grab the username, leaving the template rendering function with no logic.

## Setup

With these three services and one component in place, time to wire things up:

```{literalinclude} ../../../examples/basic/inject_service.py
:start-at: registry.register_factory(Database
:end-at: registry.register_factory(Users
```

Here we see the use of `auto()`, as `Users` injects a dependency from `Database`.

Then a request comes in, so we put it in the container:

```{literalinclude} ../../../examples/basic/inject_service.py
:start-at: request =
:end-at:  container.register_local_value(Request
```

Our `html()` call passes in the container as the "context" value:

```{literalinclude} ../../../examples/basic/inject_service.py
:start-at: response = html(
:end-at: response = html(
```

Our modified `tdom_svcs.html()` function checks for any injection and passes in the `Users` service.

## Full source code

```{literalinclude} ../../../examples/basic/inject_service.py
```
