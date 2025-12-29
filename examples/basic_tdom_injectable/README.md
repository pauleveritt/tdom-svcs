# Example: Basic tdom-svcs with @injectable (Class Components)

This example demonstrates the **recommended production pattern** for tdom-svcs: class components with `@injectable` decorator, automatic scanning, and `ComponentLookup` service.

## Key Concepts

- **Class components** - Dataclass components that can be registered by name
- **@injectable decorator** - Marks components for automatic discovery
- **scan_components()** - Automatically discovers and registers decorated components
- **ComponentLookup** - Resolves components by string name
- **HopscotchInjector** - Production injector with resource/location support
- **Inject[]** - Automatic dependency injection

## What This Example Shows

✅ How to mark components with `@injectable`
✅ How to scan packages for components
✅ How ComponentLookup resolves components by name
✅ How dependencies are automatically injected
✅ Production-ready pattern with HopscotchInjector

## What Makes This Production-Ready

This example uses:
- **Class components** (not functions) - Can be registered by string name
- **HopscotchInjector** (not KeywordInjector) - Supports resource/location resolution
- **ComponentLookup** - Enables template string lookup like `<Button>`
- **Automatic scanning** - No manual registration needed
- **Type-safe** - Full IDE autocomplete and type checking

## When to Use This Pattern

Use this pattern for:
- ✅ Production applications
- ✅ Reusable component libraries
- ✅ Template-based rendering with component lookup
- ✅ Components that need resource or location-based resolution

## Structure

- `app.py` - Standard setup: registry, scanning, container
- `site.py` - Component resolution demonstration
- `components/` - Dataclass components with `@injectable`
- `services/` - Service classes for dependency injection

## Running

```bash
python -m examples.basic_tdom_injectable.site
```

## Comparison

This is the **recommended pattern** for production use. Compare with:
- `basic_tdom_svcs` - Educational example with function components
- `component_discovery` - More advanced scanning scenarios
- `resource_based_components` - Multi-implementation with resources
- `location_based_components` - Route-specific components
