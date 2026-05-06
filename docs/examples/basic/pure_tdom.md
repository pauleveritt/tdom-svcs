# Pure tdom-svcs Rendering

This example shows the smallest useful `tdom-svcs` component: a plain function with explicit props.

## Component

The component returns a PEP 750 template string:

```{example-snippet} basic/pure_tdom.py#greeting-component
```

## Rendering

Pass the component and props in the template expression:

```{example-snippet} basic/pure_tdom.py#render-call
```

This implementation is purely functional. No container is needed until you opt into dependency injection.

## Full source code

```{example-source} basic/pure_tdom
```
