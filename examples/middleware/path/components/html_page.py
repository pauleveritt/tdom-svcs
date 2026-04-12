"""HTMLPage component that composes Head and Body."""

from dataclasses import dataclass

from markupsafe import Markup
from svcs_hopscotch.injectors import injectable

from examples.middleware.path.components.body import Body
from examples.middleware.path.components.head import Head
from tdom_svcs import html


@injectable
@dataclass
class HTMLPage:
    """Full HTML page component composing Head and Body.

    Demonstrates component composition where the page assembles
    child components, each of which may have their own assets.
    """

    def __call__(self, context: object = None) -> str | Markup:
        """Render complete HTML document."""
        return html(
            t"""
            <!DOCTYPE html>
            <html>
                <{Head} />
                <{Body} />
            </html>
        """,
            context=context,
        )
