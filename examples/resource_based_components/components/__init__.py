"""Resource-based dashboard components."""

from dataclasses import dataclass

from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from tdom import Node
from tdom_svcs import html

from examples.resource_based_components.services.analytics import AnalyticsService
from examples.resource_based_components.services.contexts import (
    AdminContext,
    CustomerContext,
)
from examples.resource_based_components.services.user import UserService


@injectable(resource=CustomerContext)
@dataclass
class CustomerDashboard:
    """Dashboard for customer users."""

    user: Inject[UserService]
    analytics: Inject[AnalyticsService]

    def __call__(self) -> Node:
        user_data = self.user.get_current_user()
        stats = self.analytics.get_stats()
        name = user_data["name"]
        visits = stats["visits"]
        return html(t"<div>Customer Dashboard for {name}: {visits} visits</div>")


@injectable(resource=AdminContext)
@dataclass
class AdminDashboard:
    """Dashboard for admin users."""

    analytics: Inject[AnalyticsService]

    def __call__(self) -> Node:
        stats = self.analytics.get_stats()
        visits = stats["visits"]
        return html(t"<div>Admin Dashboard: Total visits {visits}</div>")
