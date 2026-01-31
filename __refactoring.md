I will refactor `examples/inject_service.py` to demonstrate dependency injection between the `User` and `Database` services using `svcs` and `svcs-di`.

### Overview
This refactoring will decouple user-specific logic from the low-level database storage. The `User` service will become the primary interface for user operations, while the `Database` service will focus on data persistence and initialization. This demonstrates how `svcs-di` automatically resolves dependencies between services when using the `auto()` wrapper.

### Key Changes
- **`examples/inject_service.py`**
    - **Imports**: Add `Registry`, `Container` from `svcs`, and `Inject`, `auto` from `svcs_di`.
    - **`Database` Service**: 
        - Switch from `_users` field to a public `users` field.
        - Use `__post_init__` to populate `users` from `DEFAULT_USERS`.
        - Remove `get_user` and `list_users` (migrating them to the `User` service).
    - **`User` Service**:
        - New dataclass using `Inject[Database]` to access the data store.
        - Implement `get_user` and `list_user` methods that operate on the injected database.
    - **`main` Function**:
        - Setup `svcs.Registry`.
        - Register `Database` as a factory.
        - Register `User` as a factory using `auto(User)`.
        - Demonstrate service resolution via a `svcs.Container`.

### Implementation Steps
1. **Update Imports**: Ensure `svcs` and `svcs_di` utilities are available.
2. **Refactor `Database`**: 
    - Declare `users: Users = field(init=False)`.
    - Implement `__post_init__` to copy the default data.
    - Delete the old user-access methods.
3. **Implement `User` Service**:
    - Create the `@dataclass` with the `db: Inject[Database]` field.
    - Add `get_user` and `list_user` methods.
4. **Update `main` Logic**:
    - Initialize the registry and register both services.
    - Create a container and retrieve the `User` service.
    - Add print statements or assertions to verify the services are working correctly together.

### Technical Considerations
- **`auto(User)`**: This is critical as it instructs `svcs-di` to inspect the `User` class for `Inject` type hints and automatically provide those dependencies when the service is requested from the container.
- **Service Lifetime**: By using `register_factory`, we ensure instances can be managed per container (request-scoped) if desired.

### Success Criteria
- `Database` correctly initializes its `users` attribute in `__post_init__`.
- `User` service successfully retrieves and uses the injected `Database` instance.
- The example runs to completion, demonstrating successful multi-level dependency injection.

Please toggle to Act mode if you are ready for me to implement these changes.