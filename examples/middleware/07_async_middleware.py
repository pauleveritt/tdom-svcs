"""
Async Middleware Example.

This example demonstrates:
1. Async middleware implementation with async __call__
2. Mixed sync and async middleware in same execution chain
3. Automatic async detection via inspect.iscoroutinefunction()
4. Priority-based ordering maintained for async middleware
5. Async error handling
6. Real-world async use cases (database queries, API calls)

The middleware system automatically detects and awaits async middleware,
allowing seamless mixing of sync and async middleware in the same chain.
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, cast

from tdom_svcs.services.middleware import Context, MiddlewareManager
from tdom_svcs.types import Component


# Sync middleware (regular)
@dataclass
class SyncLoggingMiddleware:
    """Synchronous logging middleware for comparison."""

    priority: int = -10

    def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Log synchronously."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )
        print(f"[SYNC-LOG] Processing {component_name}")
        return props


# Async middleware
@dataclass
class AsyncDatabaseMiddleware:
    """
    Async middleware that fetches data from database.

    In real applications, this might:
    - Query user permissions from database
    - Fetch related data for component
    - Check cache and fall back to database
    """

    priority: int = -5

    async def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Fetch data from database asynchronously."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )

        print(f"[ASYNC-DB] Querying database for {component_name}...")

        # Simulate async database query
        await asyncio.sleep(0.1)

        # Add fetched data to props
        props["_db_user"] = {"id": 123, "name": "John Doe", "role": "admin"}
        print(f"[ASYNC-DB] Database query complete")

        return props


@dataclass
class AsyncAPIMiddleware:
    """
    Async middleware that calls external API.

    In real applications, this might:
    - Fetch data from external services
    - Validate credentials with auth service
    - Check feature flags from remote service
    """

    priority: int = 0

    async def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Call external API asynchronously."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )

        print(f"[ASYNC-API] Calling external API for {component_name}...")

        # Simulate async API call
        await asyncio.sleep(0.15)

        # Add API response to props
        props["_api_data"] = {
            "feature_flags": {"new_ui": True, "dark_mode": False},
            "quota": {"used": 42, "limit": 100},
        }
        print(f"[ASYNC-API] API call complete")

        return props


@dataclass
class AsyncValidationMiddleware:
    """
    Async middleware that validates props asynchronously.

    In real applications, this might:
    - Check credentials against auth service
    - Validate data against remote schema
    - Verify permissions with policy engine
    """

    priority: int = 5

    async def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Validate props asynchronously."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )

        print(f"[ASYNC-VALIDATE] Validating {component_name} props...")

        # Simulate async validation
        await asyncio.sleep(0.05)

        # Check for invalid prop
        if "invalid" in props:
            print(f"[ASYNC-VALIDATE] Validation failed - halting execution")
            return None

        print(f"[ASYNC-VALIDATE] Validation passed")
        return props


# Sync middleware that runs after async middleware
@dataclass
class SyncTransformMiddleware:
    """
    Synchronous middleware that transforms async-enriched props.

    This demonstrates that sync middleware can work with data
    added by async middleware - execution order is maintained.
    """

    priority: int = 10

    def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Transform props synchronously."""
        print(f"[SYNC-TRANSFORM] Transforming props...")

        # Access data added by async middleware
        if "_db_user" in props:
            user = props["_db_user"]
            props["_display_name"] = f"{user['name']} ({user['role']})"
            print(f"[SYNC-TRANSFORM] Added display name: {props['_display_name']}")

        if "_api_data" in props:
            api_data = props["_api_data"]
            props["_feature_enabled"] = api_data["feature_flags"]["new_ui"]
            print(f"[SYNC-TRANSFORM] Added feature flag: {props['_feature_enabled']}")

        return props


# Async error handling middleware
@dataclass
class AsyncErrorHandlerMiddleware:
    """
    Async middleware that handles errors with async operations.

    This demonstrates error handling in async middleware context.
    """

    priority: int = 100

    async def __call__(
        self,
        component: Component,
        props: dict[str, Any],
        context: Context,
    ) -> dict[str, Any] | None:
        """Handle errors asynchronously."""
        component_name = (
            component.__name__ if hasattr(component, "__name__") else str(component)
        )

        try:
            # Check for error conditions
            if "error" in props:
                # Simulate async error logging
                await asyncio.sleep(0.05)
                print(f"[ASYNC-ERROR] Logged error to remote service")
                return None

            print(f"[ASYNC-ERROR] No errors detected for {component_name}")
            return props

        except Exception as e:
            # Simulate async error notification
            await asyncio.sleep(0.05)
            print(f"[ASYNC-ERROR] Sent error notification: {e}")
            return None


# Example components
class Dashboard:
    """Example dashboard component."""

    def __init__(self, title: str, **kwargs):
        self.title = title
        self.props = kwargs


class UserProfile:
    """Example user profile component."""

    def __init__(self, user_id: int, **kwargs):
        self.user_id = user_id
        self.props = kwargs


async def main():
    """Demonstrate async middleware patterns."""
    print("=" * 70)
    print("Async Middleware Example")
    print("=" * 70)

    # Create manager
    manager = MiddlewareManager()

    # Register mixed sync and async middleware
    print("\nRegistering mixed sync and async middleware...")
    manager.register_middleware(SyncLoggingMiddleware())
    manager.register_middleware(AsyncDatabaseMiddleware())
    manager.register_middleware(AsyncAPIMiddleware())
    manager.register_middleware(AsyncValidationMiddleware())
    manager.register_middleware(SyncTransformMiddleware())
    manager.register_middleware(AsyncErrorHandlerMiddleware())

    print("\nMiddleware chain:")
    print("  1. SyncLoggingMiddleware (priority: -10) [SYNC]")
    print("  2. AsyncDatabaseMiddleware (priority: -5) [ASYNC]")
    print("  3. AsyncAPIMiddleware (priority: 0) [ASYNC]")
    print("  4. AsyncValidationMiddleware (priority: 5) [ASYNC]")
    print("  5. SyncTransformMiddleware (priority: 10) [SYNC]")
    print("  6. AsyncErrorHandlerMiddleware (priority: 100) [ASYNC]")

    # Create context
    context: Context = cast(Context, {"config": {}})

    # Test 1: Successful execution with mixed sync/async
    print("\n" + "=" * 70)
    print("Test 1: Dashboard with valid props (mixed sync/async)")
    print("=" * 70)
    props = {"title": "Main Dashboard"}
    result = await manager.execute_async(Dashboard, props, context)

    if result:
        print(f"\nSuccess! Final props keys: {list(result.keys())}")
        print(f"  - Original: {list([k for k in result.keys() if not k.startswith('_')])}")
        print(f"  - Added by middleware: {list([k for k in result.keys() if k.startswith('_')])}")
        if "_display_name" in result:
            print(f"  - Display name: {result['_display_name']}")
        if "_feature_enabled" in result:
            print(f"  - Feature enabled: {result['_feature_enabled']}")
    else:
        print(f"\nExecution halted by middleware")

    # Test 2: Validation failure in async middleware
    print("\n" + "=" * 70)
    print("Test 2: UserProfile with invalid props (async validation fails)")
    print("=" * 70)
    props = {"user_id": 456, "invalid": True}
    result = await manager.execute_async(UserProfile, props, context)

    if result:
        print(f"\nSuccess! Final props: {result}")
    else:
        print(f"\nExecution halted by async validation middleware")

    # Test 3: Error handling in async middleware
    print("\n" + "=" * 70)
    print("Test 3: Dashboard with error prop (async error handling)")
    print("=" * 70)
    props = {"title": "Error Dashboard", "error": "Something went wrong"}
    result = await manager.execute_async(Dashboard, props, context)

    if result:
        print(f"\nSuccess! Final props: {result}")
    else:
        print(f"\nExecution halted by async error handler")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: Key Async Middleware Concepts")
    print("=" * 70)
    print("""
1. ASYNC MIDDLEWARE DETECTION
   - System automatically detects async via inspect.iscoroutinefunction()
   - No special registration needed - just use async def __call__

2. MIXED SYNC AND ASYNC
   - Sync and async middleware can coexist in same chain
   - System automatically awaits async middleware
   - Execution order maintained regardless of sync/async

3. PRIORITY ORDERING
   - Priority system works identically for sync and async
   - Lower priority executes first (regardless of sync/async)
   - Example: -10 (sync) -> -5 (async) -> 0 (async) -> 10 (sync)

4. ASYNC USE CASES
   - Database queries (AsyncDatabaseMiddleware)
   - API calls (AsyncAPIMiddleware)
   - Remote validation (AsyncValidationMiddleware)
   - Async error logging/notification (AsyncErrorHandlerMiddleware)

5. DATA FLOW
   - Async middleware enriches props with fetched data
   - Subsequent sync middleware can access async-fetched data
   - Props flow through chain maintaining all additions

6. ERROR HANDLING
   - Async middleware can halt execution by returning None
   - Async error handlers can perform async operations (logging, notifications)
   - Exception handling works same as sync middleware

7. PERFORMANCE
   - Async middleware enables concurrent I/O operations
   - No blocking of execution thread during async operations
   - Essential for scalable applications with external dependencies
""")

    print("=" * 70)
    print("Example Complete")
    print("=" * 70)
    print("\nNote: Use await manager.execute_async() when using async middleware")
    print("      Use manager.execute() for sync-only middleware chains")


if __name__ == "__main__":
    # Run async main
    asyncio.run(main())
