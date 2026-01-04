# Location-Based Components Example

This example demonstrates **location-based component resolution** using `@injectable(location=...)` from svcs-di.

## Concept

Different components are registered for different URL paths/locations:
- `HomePage` for `/`
- `AdminPanel` for `/admin`
- `UserManagement` for `/admin/users`

HopscotchInjector automatically resolves the correct component based on the location (PurePath) in context.

## Key Pattern

```python
from pathlib import PurePath

# Define components with location metadata
@injectable(location=PurePath("/"))
@dataclass
class HomePage:
    def __call__(self) -> str:
        return "Home view"

@injectable(location=PurePath("/admin"))
@dataclass
class AdminPanel:
    def __call__(self) -> str:
        return "Admin view"

# Use with location context
container.register_value(PurePath, PurePath("/admin"))
panel = container.get(AdminPanel)  # Gets admin-specific component
```

## Running

```bash
uv run python -m examples.location_based_components.app
```
