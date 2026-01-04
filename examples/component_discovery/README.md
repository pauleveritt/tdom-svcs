# Component Discovery Example

This example demonstrates automatic component discovery using `@injectable` decorator and direct type-based resolution with HopscotchInjector.

## Key Concepts

- Multiple components with `@injectable` decorator
- Components with different dependency patterns
- Direct type-based resolution (no strings!)
- Dependency injection via `Inject[]` type hints

## What This Example Shows

✅ Component with no dependencies (Button)
✅ Component with one dependency (UserProfile)
✅ Component with multiple dependencies (AdminPanel)
✅ Mixed regular and injected parameters
✅ Direct type-based component resolution

## Structure

- `app.py` - Setup and component resolution
- `site.py` - Service registration
- `components/` - Three example components showing different patterns
- `services/` - DatabaseService and AuthService

## Running

```bash
uv run python -m examples.component_discovery.app
```

## Pattern

```python
# Components are decorated with @injectable
@injectable
@dataclass
class AdminPanel:
    db: Inject[DatabaseService]
    auth: Inject[AuthService]

# Resolve directly by type
container = Container(registry)
panel = container.get(AdminPanel)  # DI happens automatically!
```
