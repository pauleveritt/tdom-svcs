"""Dashboard components with resource-based registration."""

from dataclasses import dataclass

from svcs_di import Inject
from svcs_di.injectors.decorators import injectable

from direct_decorator.contexts import AdminContext, CustomerContext
from direct_decorator.services import ThemeService


@dataclass
class CustomerDashboard:
    """Dashboard for customer context."""

    theme: Inject[ThemeService]
    title: str = "Customer Dashboard"

    def __call__(self) -> str:
        """Render customer dashboard."""
        color = self.theme.get_theme("customer") if self.theme else "blue"
        return f"""
        <div class="dashboard" style="border: 3px solid {color}">
            <h1>{self.title}</h1>
            <p>Customer-specific dashboard content</p>
        </div>
        """.strip()


@dataclass
class AdminDashboard:
    """Dashboard for admin context."""

    theme: Inject[ThemeService]
    title: str = "Admin Dashboard"

    def __call__(self) -> str:
        """Render admin dashboard."""
        color = self.theme.get_theme("admin") if self.theme else "red"
        return f"""
        <div class="dashboard" style="border: 3px solid {color}">
            <h1>{self.title}</h1>
            <p>Admin-specific dashboard content</p>
        </div>
        """.strip()


# Apply decorators with resource metadata
# Note: injectable() modifies the class in-place, no reassignment needed
injectable(resource=CustomerContext)(CustomerDashboard)
injectable(resource=AdminContext)(AdminDashboard)
