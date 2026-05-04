"""Middleware support for tdom templates."""

import inspect
from typing import Any, cast, overload

from svcs_hopscotch.injectors.decorators import (
    CategoryInput,
    InjectableMetadata,
    InjectableTarget,
    injectable,
)

from tdom_svcs.types import (
    AsyncMiddleware,
    Middleware,
    MiddlewareMap,
    Props,
    PropsResult,
    Target,
)

HOOKABLE_MIDDLEWARE_ATTR = "__hookable_middleware__"


class middleware(injectable):
    """Decorator for marking middleware implementations."""

    kind = "middleware"


class hookable(injectable):
    """Decorator for marking targets with per-target middleware hooks."""

    kind = "hookable"
    _middleware: MiddlewareMap

    @overload
    def __new__(cls, target: InjectableTarget) -> InjectableTarget: ...

    @overload
    def __new__(
        cls,
        *,
        for_: type | None = None,
        resource: type | None = None,
        location: Any = None,
        categories: CategoryInput = None,
        middleware: MiddlewareMap | None = None,
    ) -> "hookable": ...

    def __new__[T: InjectableTarget](
        cls,
        target: T | None = None,
        *,
        for_: type | None = None,
        resource: type | None = None,
        location: Any = None,
        categories: CategoryInput = None,
        middleware: MiddlewareMap | None = None,
    ) -> T | "hookable":
        instance = cast(
            hookable,
            super().__new__(
                cls,
                for_=for_,
                resource=resource,
                location=location,
                categories=categories,
            ),
        )
        instance._middleware = middleware or {}
        if target is not None:
            return instance(target)
        return instance

    def __init__(
        self,
        target: InjectableTarget | None = None,
        *,
        for_: type | None = None,
        resource: type | None = None,
        location: Any = None,
        categories: CategoryInput = None,
        middleware: MiddlewareMap | None = None,
    ) -> None:
        super().__init__(
            target,
            for_=for_,
            resource=resource,
            location=location,
            categories=categories,
        )

    def post_decorate(
        self, target: InjectableTarget, metadata: InjectableMetadata
    ) -> None:
        """Store phase middleware on the decorated target."""
        if self._middleware:
            setattr(target, HOOKABLE_MIDDLEWARE_ATTR, self._middleware)


def register_middleware(
    registry: Any,
    middleware_type: type[Middleware | AsyncMiddleware],
    categories: CategoryInput = None,
) -> None:
    """Register a middleware type with the registry."""
    registry.register_implementation(
        middleware_type,
        middleware_type,
        kind="middleware",
        categories=categories,
    )


def register_hookable(
    registry: Any,
    target: type,
    middleware: MiddlewareMap | None = None,
    categories: CategoryInput = None,
) -> None:
    """Register a hookable target with optional phase middleware."""
    if middleware:
        setattr(target, HOOKABLE_MIDDLEWARE_ATTR, middleware)

    registry.register_implementation(
        target,
        target,
        kind="hookable",
        categories=categories,
    )


def get_middleware_types(registry: Any) -> list[type]:
    """Return all middleware types registered by kind."""
    return registry.get_by_kind("middleware")


def execute_middleware(
    target: Target, props: Props, container: Any, context: Any = None
) -> PropsResult:
    """Execute global middleware synchronously."""
    middleware_instances: list[Middleware | AsyncMiddleware] = [
        container.inject(mw_type)
        for mw_type in get_middleware_types(container.registry)
    ]
    middleware_instances.sort(key=lambda mw: mw.priority)

    current_props: Props = props
    for mw in middleware_instances:
        if inspect.iscoroutinefunction(mw.__call__):
            raise RuntimeError(
                f"Async middleware {type(mw).__name__} cannot be executed in sync context. "
                "Use execute_middleware_async instead."
            )
        sync_mw = cast(Middleware, mw)
        result = sync_mw(target, current_props, context)
        if result is None:
            return None
        current_props = result

    return current_props


async def execute_middleware_async(
    target: Target, props: Props, container: Any, context: Any = None
) -> PropsResult:
    """Execute global middleware with async support."""
    middleware_instances: list[Middleware | AsyncMiddleware] = [
        container.inject(mw_type)
        for mw_type in get_middleware_types(container.registry)
    ]
    middleware_instances.sort(key=lambda mw: mw.priority)

    current_props: Props = props
    for mw in middleware_instances:
        if inspect.iscoroutinefunction(mw.__call__):
            async_mw = cast(AsyncMiddleware, mw)
            result = await async_mw(target, current_props, context)
        else:
            sync_mw = cast(Middleware, mw)
            result = sync_mw(target, current_props, context)
        if result is None:
            return None
        current_props = result

    return current_props


def execute_target_middleware(
    target: Target,
    props: Props,
    container: Any,
    phase: str = "before",
    context: Any = None,
) -> PropsResult:
    """Execute phase middleware attached to a target."""
    middleware_map: MiddlewareMap | None = getattr(
        target, HOOKABLE_MIDDLEWARE_ATTR, None
    )
    if not middleware_map:
        return props

    middleware_instances: list[Middleware] = [
        container.inject(mw_type) for mw_type in middleware_map.get(phase, [])
    ]
    middleware_instances.sort(key=lambda mw: mw.priority)

    current_props: Props = props
    for mw in middleware_instances:
        result: PropsResult = mw(target, current_props, context)  # type: ignore[misc]
        if result is None:
            return None
        current_props = result

    return current_props
