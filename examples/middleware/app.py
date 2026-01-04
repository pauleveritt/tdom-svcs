from svcs import Registry, Container
from examples.middleware import site
from examples.middleware.components import Button
from tdom_svcs.services.middleware import MiddlewareManager, get_component_middleware


def main() -> str:
    registry = Registry()
    context = {"config": {"debug": True}}

    # Custom setup from site.py
    site.svcs_setup(registry, context)

    with Container(registry) as container:
        from examples.middleware.site import GlobalLoggingMiddleware
        manager = container.get(MiddlewareManager)
        manager.register_middleware(GlobalLoggingMiddleware())

        props = {"title": "Submit"}
        # Execute global middleware
        result = manager.execute(Button, props, context)

        # Execute per-component middleware
        if result is not None:
            component_middleware = get_component_middleware(Button)
            for mw in component_middleware.get("pre_resolution", []):
                result = mw(Button, result, context)
                if result is None:
                    break

        return str(result)


if __name__ == "__main__":
    print(main())
