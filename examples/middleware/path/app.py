"""Path middleware example.

Demonstrates:
- Tracking component locations during rendering
- Collecting static asset references from rendered HTML
- Rewriting relative paths to absolute paths for browser consumption
"""

from svcs_di.injectors import HopscotchContainer, HopscotchRegistry
from svcs_di.injectors.scanning import scan

from examples.common import Request
from examples.middleware.path import components, services
from examples.middleware.path.components import Head, HTMLPage
from tdom_svcs import html
from tdom_svcs.services.path import PathCollector


def rewrite_paths(
    html_string: str, collector: PathCollector, static_prefix: str
) -> str:
    """Rewrite relative asset paths to absolute paths.

    Takes rendered HTML with relative paths like `./static/styles.css` and
    transforms them to absolute paths like `/_static/module/path/static/styles.css`.

    Args:
        html_string: The rendered HTML with relative paths
        collector: PathCollector containing asset references
        static_prefix: URL prefix for static assets (e.g., "/_static")

    Returns:
        HTML with rewritten absolute paths
    """
    result = html_string
    for asset in collector.assets:
        # Build the absolute path from the module path
        absolute_path = f"{static_prefix}/{asset.module_path}"
        # Replace the relative path with the absolute path
        result = result.replace(f'"{asset.relative_path}"', f'"{absolute_path}"')
    return result


def main() -> str:
    """Demonstrate path collection and rewriting."""
    # Setup registry and scan for services/components
    registry = HopscotchRegistry()
    scan(registry, services, components)

    # Create PathCollector service
    collector = PathCollector()
    registry.register_value(PathCollector, collector)

    with HopscotchContainer(registry) as container:
        container.register_local_value(Request, Request(user_id="1"))

        # Render the page (paths are still relative)
        response = html(t"<{HTMLPage} />", context=container)
        original_html = str(response)

        # Verify the original HTML has relative paths
        assert 'href="./static/styles.css"' in original_html
        assert 'src="./static/script.js"' in original_html

        # Register components and collect their assets
        head_location = collector.register_component(Head)
        head_instance = container.get(Head)
        head_node = head_instance()
        collector.collect_from_node(head_node, head_location)

        # Verify assets were collected
        assert len(collector.assets) == 2
        relative_paths = {ref.relative_path for ref in collector.assets}
        assert "./static/styles.css" in relative_paths
        assert "./static/script.js" in relative_paths

        # Verify module paths are correctly resolved
        module_paths = {str(ref.module_path) for ref in collector.assets}
        assert (
            "examples/middleware/path/components/head/static/styles.css" in module_paths
        )
        assert (
            "examples/middleware/path/components/head/static/script.js" in module_paths
        )

        # Rewrite paths for browser consumption
        rewritten_html = rewrite_paths(original_html, collector, "/_static")

        # Verify the rewritten HTML has absolute paths
        assert (
            'href="/_static/examples/middleware/path/components/head/static/styles.css"'
            in rewritten_html
        )
        assert (
            'src="/_static/examples/middleware/path/components/head/static/script.js"'
            in rewritten_html
        )

        return rewritten_html


if __name__ == "__main__":
    print(main())
