# Props Priority

In the [previous example](inject_service) we saw a `Greeting` component that injected the entire `Users` service, when
all it needed to render was the name of the current user.

In this example, we'll show how to write dataclasses that minimize the dependency surface area, clearly showing
specifically what is needed. This then allows a caller to override that single value by passing in a prop.

## Verbose but clear component

What does `Greeting` *really* need from the outside world in order to render? Let's change the component dataclass to be
a *lot* more specific:

```{literalinclude} ../../../examples/basic/props_priority.py
:start-after: A component that injects the Users service
:end-at: return html(
```

We're now saying two things:

- `current_user` is what the component *really* needs to find
- `Greeting` will need the `Users` service to find `current_user`
- The `__post_init__` will do the calculation and store the value, *before* the method that renders

## Two usages

With this change, we can now use the component in two ways. First, by passing in a prop that says, for *this* usage,
here's the value:

```{literalinclude} ../../../examples/basic/props_priority.py
:start-after: Override the user_name prop
:end-at: assert "Mary"
```

Otherwise, if the caller doesn't pass in a prop, the component will get it from the container:

```{literalinclude} ../../../examples/basic/props_priority.py
:start-after: Let the injector
:end-at: assert "Alice"
```

## Useful...but magical

There's actually a lot to unpack in this pattern:

- *Make the dependency clear*. You can scan the dataclass fields and see that `current_user` is the actual data needed
  for the template.
- *Props override*. What if you aren't using an injector? Or want to override the value for a specific usage? Making a
  fine-grained prop allows this.
- *Logic/data before rendering*. You can construct your component instance and test that your data is correct, rather
  than picking apart a rendered template.
- *Replaceable components*. This project lets you replace a component. Maybe you want to keep the contract and just
  change the rendering. You can subclass the compnent and change the `__call__`.
- *Agent-friendly* Ok, this is a guess. But being extra-specific on structure and type might help coding agents inspect
  components and get it right the first time.

There are, of course, tradeoffs:

- *Verbose*. Dataclass components are more typing than function components, and this pattern adds to it. On the flip
  side, this might actually be easier for *reading*, as you don't have to go scan the `__call__` to learn what the
  component wants. "It's there on the tin."
- *Magic*. `svcs-di` already brought in magic. We're piling on, by detecting the `InitVar` pattern. That said, the magic
  fits with dataclass machinery. Agents, for example, will already be familiar with reading and writing these dataclass
  patterns.

## Full source code

```{literalinclude} ../../../examples/basic/props_priority.py
```
