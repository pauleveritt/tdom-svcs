# Example: Component Discovery and Registration

This example demonstrates the complete workflow for automatic component discovery using `@injectable` decorator and `scan_components()` function. It shows advanced scenarios beyond the basic example.

## Key Concepts

- Multiple components in a package
- Components with different dependency patterns
- Mixed regular and injected parameters
- Automatic scanning and registration
- ComponentLookup resolution

## What This Example Shows

✅ Multiple component classes in components/ package
✅ Components with no dependencies (Button)
✅ Components with one dependency (UserProfile)
✅ Components with multiple dependencies (AdminPanel)
✅ Mixing regular parameters with Inject[]
✅ Automatic discovery via scan_components()

## Structure

- `app.py` - Standard setup with scanning
- `site.py` - Demonstrates resolving different components
- `components/` - Three example components
- `services/` - DatabaseService and AuthService

## Running

```bash
python -m examples.component_discovery.site
```

## Comparison

- `basic_tdom_injectable` - Simpler introduction
- This example - More components, more patterns
- `resource_based_components` - Adds resource-based resolution
