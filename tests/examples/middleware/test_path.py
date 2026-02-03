"""Tests for path middleware example and PathCollector service."""

from pathlib import Path, PurePosixPath

from tdom import html

from examples.middleware.path.components.head import Head
from examples.middleware.path.components.body import Body
from tdom_svcs.services.path import ComponentLocation, PathCollector


# Use real components for testing instead of mocks with fake modules
MockComponent = Head
AnotherComponent = Body


class TestComponentLocation:
    """Tests for ComponentLocation dataclass."""

    def test_create_component_location(self):
        """Test creating a ComponentLocation."""
        location = ComponentLocation(
            component_type=MockComponent,
            module_name="examples.middleware.path.components.head",
            file_path=Path("/some/path/head.py"),
        )

        assert location.component_type is MockComponent
        assert location.module_name == "examples.middleware.path.components.head"
        assert location.file_path == Path("/some/path/head.py")

    def test_component_location_hashable(self):
        """Test ComponentLocation is hashable based on component type."""
        loc1 = ComponentLocation(
            component_type=MockComponent,
            module_name="mod1",
            file_path=Path("/path1"),
        )
        loc2 = ComponentLocation(
            component_type=MockComponent,
            module_name="mod2",  # Different module name, same type
            file_path=Path("/path2"),
        )

        # Same component type = same hash
        assert hash(loc1) == hash(loc2)

        # Can be used in sets
        locations = {loc1, loc2}
        assert len(locations) == 1  # Deduplicated

    def test_component_location_equality(self):
        """Test ComponentLocation equality based on component type."""
        loc1 = ComponentLocation(
            component_type=MockComponent,
            module_name="mod1",
            file_path=Path("/path1"),
        )
        loc2 = ComponentLocation(
            component_type=MockComponent,
            module_name="mod2",
            file_path=Path("/path2"),
        )
        loc3 = ComponentLocation(
            component_type=AnotherComponent,
            module_name="mod1",
            file_path=Path("/path1"),
        )

        assert loc1 == loc2  # Same component type
        assert loc1 != loc3  # Different component type


class TestPathCollector:
    """Tests for PathCollector service."""

    def test_register_component(self):
        """Test registering a component."""
        collector = PathCollector()
        location = collector.register_component(MockComponent)

        assert location.component_type is MockComponent
        assert location.module_name == "examples.middleware.path.components.head"
        assert MockComponent in [loc.component_type for loc in collector.components]

    def test_register_component_deduplication(self):
        """Test registering the same component twice doesn't duplicate."""
        collector = PathCollector()

        loc1 = collector.register_component(MockComponent)
        loc2 = collector.register_component(MockComponent)

        assert len(collector.components) == 1
        assert loc1.component_type == loc2.component_type

    def test_register_multiple_components(self):
        """Test registering multiple different components."""
        collector = PathCollector()

        collector.register_component(MockComponent)
        collector.register_component(AnotherComponent)

        assert len(collector.components) == 2
        types = {loc.component_type for loc in collector.components}
        assert MockComponent in types
        assert AnotherComponent in types

    def test_register_asset(self):
        """Test registering an asset reference."""
        collector = PathCollector()
        location = collector.register_component(MockComponent)

        asset_ref = collector.register_asset(location, "./static/styles.css")

        assert asset_ref.relative_path == "./static/styles.css"
        assert asset_ref.module_path == PurePosixPath(
            "examples/middleware/path/components/head/static/styles.css"
        )
        assert asset_ref.component_location is location
        assert len(collector.assets) == 1

    def test_collect_from_node_link_tag(self):
        """Test collecting assets from link tags."""
        collector = PathCollector()
        location = collector.register_component(MockComponent)

        node = html(t'<link rel="stylesheet" href="./static/styles.css">')
        collector.collect_from_node(node, location)

        assert len(collector.assets) == 1
        asset = next(iter(collector.assets))
        assert asset.relative_path == "./static/styles.css"

    def test_collect_from_node_script_tag(self):
        """Test collecting assets from script tags."""
        collector = PathCollector()
        location = collector.register_component(MockComponent)

        node = html(t'<script src="./static/app.js"></script>')
        collector.collect_from_node(node, location)

        assert len(collector.assets) == 1
        asset = next(iter(collector.assets))
        assert asset.relative_path == "./static/app.js"

    def test_collect_from_node_multiple_assets(self):
        """Test collecting multiple assets from a node tree."""
        collector = PathCollector()
        location = collector.register_component(MockComponent)

        node = html(
            t"""
            <head>
                <link rel="stylesheet" href="./static/styles.css">
                <script src="./static/app.js"></script>
            </head>
        """
        )
        collector.collect_from_node(node, location)

        assert len(collector.assets) == 2
        paths = {asset.relative_path for asset in collector.assets}
        assert "./static/styles.css" in paths
        assert "./static/app.js" in paths

    def test_collect_from_node_skips_external_urls(self):
        """Test that external URLs are skipped."""
        collector = PathCollector()
        location = collector.register_component(MockComponent)

        node = html(
            t"""
            <head>
                <link rel="stylesheet" href="https://cdn.example.com/styles.css">
                <link rel="stylesheet" href="//cdn.example.com/other.css">
                <script src="http://example.com/app.js"></script>
                <link rel="stylesheet" href="./local.css">
            </head>
        """
        )
        collector.collect_from_node(node, location)

        # Only the local asset should be collected
        assert len(collector.assets) == 1
        asset = next(iter(collector.assets))
        assert asset.relative_path == "./local.css"

    def test_collect_from_node_skips_special_schemes(self):
        """Test that special URL schemes are skipped."""
        collector = PathCollector()
        location = collector.register_component(MockComponent)

        # Note: Using {{ }} to escape braces in the data: URL
        node = html(
            t"""
            <head>
                <link href="mailto:test@example.com">
                <link href="tel:+1234567890">
                <link href="data:text/css,body{{}}">
                <link href="javascript:void(0)">
                <link href="#anchor">
                <link rel="stylesheet" href="./styles.css">
            </head>
        """
        )
        collector.collect_from_node(node, location)

        # Only the local asset should be collected
        assert len(collector.assets) == 1
        asset = next(iter(collector.assets))
        assert asset.relative_path == "./styles.css"

    def test_collect_from_node_nested_structure(self):
        """Test collecting from deeply nested node structure."""
        collector = PathCollector()
        location = collector.register_component(MockComponent)

        node = html(
            t"""
            <html>
                <head>
                    <meta charset="utf-8">
                    <title>Test</title>
                    <link rel="stylesheet" href="./static/styles.css">
                </head>
                <body>
                    <div>
                        <script src="./static/app.js"></script>
                    </div>
                </body>
            </html>
        """
        )
        collector.collect_from_node(node, location)

        assert len(collector.assets) == 2

    def test_clear(self):
        """Test clearing collected data."""
        collector = PathCollector()
        location = collector.register_component(MockComponent)
        collector.register_asset(location, "./styles.css")

        assert len(collector.components) == 1
        assert len(collector.assets) == 1

        collector.clear()

        assert len(collector.components) == 0
        assert len(collector.assets) == 0


class TestPathExampleIntegration:
    """Integration tests for the path middleware example."""

    def test_example_runs(self):
        """Test that the path example runs successfully with all assertions."""
        from examples.middleware.path.app import main

        # main() contains its own assertions for:
        # - HTML renders correctly
        # - 3 components collected (HTMLPage, Head, Body)
        # - 2 assets collected (styles.css, script.js)
        # - Module paths correctly resolved
        # - Assets linked to correct component
        result = main()

        # Verify it returns an HTML string
        assert isinstance(result, str)
        assert "<!DOCTYPE html>" in result

    def test_example_renders_html(self):
        """Test that the example renders valid HTML."""
        from examples.middleware.path.app import main

        result = main()

        assert "<!DOCTYPE html>" in result
        assert "<html>" in result
        assert "<head>" in result
        assert "<body>" in result
        assert "Hello Alice!" in result

    def test_static_files_exist(self):
        """Test that the static asset files actually exist."""
        import importlib.resources

        head_resources = importlib.resources.files(
            "examples.middleware.path.components.head"
        )

        # Verify both static files exist
        styles_path = head_resources / "static" / "styles.css"
        script_path = head_resources / "static" / "script.js"

        assert styles_path.is_file(), "styles.css should exist"
        assert script_path.is_file(), "script.js should exist"
