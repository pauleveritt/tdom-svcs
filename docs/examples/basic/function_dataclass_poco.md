# Functions, dataclasses, and POCOs

In `tdom`, components can be functions, dataclasses, or plain old class objects (POCOs). This is also true for the
features shown in this project.

Let's see `context` getting "injected" in all three component flavors.

## Function component

As we saw in the [previous example](pure_tdom), a function component can ask for `context` as a parameter:

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
:start-at: def Greeting
:end-at: return
```

When rendered, the `context` argument value is passed into the function:

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
:start-at: Function component:
:end-at: in result1
```

We can see this in dataclass components. They receive the `context` as a parameter and the `__call__` does the
rendering:

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
:start-at: Dataclass component:
:end-at: in result2
```

Finally, a plain old class component:

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
:start-at: Class component:
:end-at: in result3
```

## `__post_init__` pattern

Perhaps you noticed the curious `__post_init__` pattern in the dataclass component. What's that about?

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
:start-at: @dataclass
:end-at: return html
:emphasize-lines: 3, 5-6
```

The `__post_init__` pattern is a way to initialize a dataclass after it's been created. It's useful here:

- Our component actually depends on the `user`
- Which is in the `context`
- We can't get to `user` until *after* we've been passed in the `context`
- The `__post_init__` pattern allows us to do that
- We mark context as `InitVar` to indicate it is *only* used during construction
- The `context` is then passed into `__post_init__`

We get to put `user: str` as a field, which helps signify the contract. The field says `field(init=False)` to signify
that we aren't getting it during construction -- it is assigned in `__post_init__`.

There's a larger pattern: get *all* of your template data resolved *before* calling the render function. This does two
things:

- Makes it clear *which* parts of a possibly-huge `context` you actually need
- You can get all our data set up, with the logic to make it, and then...
- More easily test the data part of your template

## Full source code

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
```
