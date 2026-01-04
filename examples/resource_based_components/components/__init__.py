"""Resource-based dashboard components."""

from dataclasses import dataclass
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from examples.resource_based_components.services.contexts import CustomerContext, AdminContext
from examples.resource_based_components.services.user import UserService
from examples.resource_based_components.services.analytics import AnalyticsService


@injectable(resource=CustomerContext)
@dataclass
class CustomerDashboard:
    """Dashboard for customer users."""

    user: Inject[UserService]
    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        user_data = self.user.get_current_user()
        stats = self.analytics.get_stats()
        return f"<div>Customer Dashboard for {user_data['name']}: {stats['visits']} visits</div>"


@injectable(resource=AdminContext)
@dataclass
class AdminDashboard:
    """Dashboard for admin users."""

    analytics: Inject[AnalyticsService]

    def __call__(self) -> str:
        stats = self.analytics.get_stats()
        return f"<div>Admin Dashboard: Total visits {stats['visits']}</div>"
