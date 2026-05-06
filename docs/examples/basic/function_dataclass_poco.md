# Functions, dataclasses, and POCOs

In `tdom`, components can be functions, dataclasses, or plain old class objects (POCOs). This is also true for the
features shown in this project.

Let's see the same greeting component expressed in all three component flavors.

## Function component

As we saw in the [previous example](pure_tdom), a function component can be rendered directly:

```{example-snippet} basic/function_dataclass_poco.py#function-component
```

When rendered, props from the template are passed into the function:

```{example-snippet} basic/function_dataclass_poco.py#render-function
```

The same shape works with a dataclass component. The template props initialize the dataclass and `__call__` renders it:

```{example-snippet} basic/function_dataclass_poco.py#dataclass-component
```

```{example-snippet} basic/function_dataclass_poco.py#render-dataclass
```

Finally, a plain old class object can expose the same callable component shape:

```{example-snippet} basic/function_dataclass_poco.py#poco-component
```

```{example-snippet} basic/function_dataclass_poco.py#render-poco
```

Each form receives the same `name` prop and renders the same template output.

## Full source code

```{example-source} basic/function_dataclass_poco
```
