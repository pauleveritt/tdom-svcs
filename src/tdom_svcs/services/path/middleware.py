"""PathMiddleware for registering components during rendering."""

from dataclasses import dataclass
from typing import Any

from svcs_di import Inject
from svcs_hopscotch.injectors import injectable

from tdom_svcs.services.path.collector import PathCollector
from tdom_svcs.types import COMPONENT_LOCATION_PROP


@injectable
@dataclass(frozen=True, kw_only=True, slots=True)
class PathMiddleware:
    """Middleware that registers components with PathCollector during rendering.

    Runs late in the middleware chain (priority=100) to let other middleware
    process props first. Stores the ComponentLocation in props for later access.
    """

    collector: Inject[PathCollector]
    priority: int = 100

    def __call__(
        self,
        component: type,
        props: dict[str, Any],
        context: Any,
    ) -> dict[str, Any]:
        """Register component and add its location to props."""
        # Register the component and get its location
        location = self.collector.register_component(component)

        # Store location in props so post-render code can access it
        props[COMPONENT_LOCATION_PROP] = location

        return props
