"""PathMiddleware for registering components during rendering."""

from dataclasses import dataclass
from typing import Any

from .collector import PathCollector


@dataclass
class PathMiddleware:
    """Middleware that registers components with PathCollector.

    PathMiddleware integrates with the middleware system to track which
    components are rendered. It runs late in the middleware chain (high
    priority number) so other middleware can process props first.

    The middleware:
    1. Registers the component with PathCollector
    2. Stores the ComponentLocation in props for later access
    3. Returns props unchanged (except for the location addition)

    Note: Asset collection from rendered Nodes is handled separately,
    not by this middleware. This middleware only tracks component registrations.

    Attributes:
        collector: PathCollector service instance (injected)
        priority: Middleware priority (100 = runs late)

    Examples:
        >>> from tdom_svcs.services.path import PathCollector, PathMiddleware
        >>> collector = PathCollector()
        >>> middleware = PathMiddleware(collector=collector)
        >>> props = middleware(MyComponent, {}, context)
        >>> props["_component_location"].module_name
        'myapp.components.my_component'
    """

    collector: PathCollector
    priority: int = 100

    def __call__(
        self,
        component: type,
        props: dict[str, Any],
        context: Any,
    ) -> dict[str, Any]:
        """Register component and add location to props.

        Args:
            component: The component being rendered
            props: Component props dictionary
            context: Middleware context (unused)

        Returns:
            Props dict with _component_location added
        """
        # Register the component and get its location
        location = self.collector.register_component(component)

        # Store location in props so post-render code can access it
        props["_component_location"] = location

        return props
