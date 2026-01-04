# Pure tdom Example

This example demonstrates the simplest possible usage of `tdom-svcs` without `svcs` or dependency injection.

## Overview

In this example, we:
- Define simple component classes that manually handle their own state.
- Create a `SimpleConfig` that implements the `tdom-svcs` configuration protocol.
- Use a plain dictionary for context.
- Manually pass context from parent components to child components.

This is useful for understanding the core mechanics of how `tdom-svcs` handles component lookup and rendering before adding the complexity of a service container.

## Key Concepts

1. **Component Lookup**: A simple function that maps strings to component classes.
2. **Config Object**: A minimal implementation of the `Config` protocol.
3. **Manual Context Propagation**: Explicitly passing data down the component tree.

## Running the Example

Run the application directly:

```bash
python examples/pure_tdom/app.py
```
