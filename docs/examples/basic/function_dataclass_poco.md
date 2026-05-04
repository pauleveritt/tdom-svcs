# Functions, dataclasses, and POCOs

In `tdom`, components can be functions, dataclasses, or plain old class objects (POCOs). This is also true for the
features shown in this project.

Let's see the same greeting component expressed in all three component flavors.

## Function component

As we saw in the [previous example](pure_tdom), a function component can be rendered directly:

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
:lines: 33-35
```

When rendered, props from the template are passed into the function:

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
:lines: 38-41
```

The same shape works with a dataclass component. The template props initialize the dataclass and `__call__` renders it:

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
:lines: 17-22
```

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
:lines: 43-45
```

Finally, a plain old class object can expose the same callable component shape:

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
:lines: 25-30
```

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
:lines: 47-49
```

Each form receives the same `name` prop and renders the same template output.

## Full source code

```{literalinclude} ../../../examples/basic/function_dataclass_poco.py
```
