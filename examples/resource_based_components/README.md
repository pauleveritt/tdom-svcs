# Resource-Based Components Example

This example demonstrates **resource-based component resolution** using `@injectable(resource=...)` from svcs-di.

## Concept

Different components can be registered for different business entities (resources):
- `CustomerDashboard` for `CustomerContext`
- `AdminDashboard` for `AdminContext`

HopscotchInjector automatically resolves the correct component based on the resource in context.

## Key Pattern

```python
# Define components with resource metadata
@injectable(resource=CustomerContext)
@dataclass
class CustomerDashboard:
    user: Inject[UserService]
    def __call__(self) -> str:
        return "Customer view"

@injectable(resource=AdminContext)
@dataclass
class AdminDashboard:
    analytics: Inject[AnalyticsService]
    def __call__(self) -> str:
        return "Admin view"

# Use with context
registry.push_resource(CustomerContext())
dashboard = container.get(Dashboard)  # Gets CustomerDashboard
```

## Running

```bash
uv run python -m examples.resource_based_components.app
```
