# Example: Basic tdom-svcs (Function Components)

This example demonstrates the simplest use of dependency injection with **function components** using `KeywordInjector`. This is an educational example showing how `Inject[]` works without component registration or lookup.

## Key Concepts

- **Function components** - Simple functions that accept `Inject[]` parameters
- **KeywordInjector** - Simple injector for direct function calls
- **No ComponentLookup** - Functions are called directly, not resolved by name
- **No @injectable** - Functions cannot use decorators (class-only)
- **Direct injection** - Services injected when calling the injector

## What This Example Shows

✅ How `Inject[]` works with function parameters
✅ Simple service registration and injection
✅ Direct function invocation (no template lookup)

## What This Example Does NOT Show

❌ Component registration by string name (class-only feature)
❌ ComponentLookup service (requires class components)
❌ @injectable decorator (class-only)
❌ Resource or location-based resolution (requires HopscotchInjector)

## When to Use This Pattern

Use function components with KeywordInjector for:
- Learning how dependency injection works
- Simple utility functions with injected dependencies
- Cases where you don't need template string lookup
- Educational examples and tutorials

## When NOT to Use This Pattern

Do not use this pattern for:
- Production components (use class components with HopscotchInjector)
- Components that need to be resolved by name in templates
- Components with resource or location-based resolution
- Reusable component libraries

## Structure

- `app.py` - Service registration and injector setup
- `site.py` - Direct function invocation demonstration
- `components/` - Function components (cannot be registered by name)
- `services/` - Service classes for dependency injection

## Running

```bash
python -m examples.basic_tdom_svcs.site
```

## Comparison

This example is intentionally simple. For production use, see:
- `basic_tdom_injectable` - Class components with @injectable and ComponentLookup
- `component_discovery` - Automatic component scanning
