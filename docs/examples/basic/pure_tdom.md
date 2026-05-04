# Pure tdom-svcs Rendering

This example shows the smallest useful `tdom-svcs` component: a plain function with explicit props.

## Component

The component returns a PEP 750 template string:

```{literalinclude} ../../../examples/basic/pure_tdom.py
:lines: 15-17
```

## Rendering

Pass the component and props in the template expression:

```{literalinclude} ../../../examples/basic/pure_tdom.py
:lines: 20-26
```

This implementation is purely functional. No container is needed until you opt into dependency injection.

## Full source code

```{literalinclude} ../../../examples/basic/pure_tdom.py
```
