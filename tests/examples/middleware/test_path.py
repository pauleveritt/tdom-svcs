"""Tests for path middleware example and PathCollector service."""

from pathlib import Path, PurePosixPath

from svcs_hopscotch.injectors import HopscotchContainer, HopscotchRegistry
from svcs_hopscotch.injectors.scanning import scan
from tdom import html

from examples.middleware.path.components.body import Body
from examples.middleware.path.components.head import Head
from tdom_svcs.services.path import (
    ComponentLocation,
    PathCollector,
    PathMiddleware,
)

# -- ComponentLocation tests --


def test_component_location_create():
    """Test creating a ComponentLocation."""
    location = ComponentLocation(
        component_type=Head,
        module_name="examples.middleware.path.components.head",
        file_path=Path("/some/path/head.py"),
    )

    assert location.component_type is Head
    assert location.module_name == "examples.middleware.path.components.head"
    assert location.file_path == Path("/some/path/head.py")


def test_component_location_hashable():
    """Test ComponentLocation is hashable based on component type."""
    loc1 = ComponentLocation(
        component_type=Head, module_name="mod1", file_path=Path("/path1")
    )
    loc2 = ComponentLocation(
        component_type=Head, module_name="mod2", file_path=Path("/path2")
    )

    assert hash(loc1) == hash(loc2)
    assert len({loc1, loc2}) == 1  # Deduplicated by component type


def test_component_location_equality():
    """Test ComponentLocation equality based on component type."""
    loc_head1 = ComponentLocation(
        component_type=Head, module_name="mod1", file_path=Path("/path1")
    )
    loc_head2 = ComponentLocation(
        component_type=Head, module_name="mod2", file_path=Path("/path2")
    )
    loc_body = ComponentLocation(
        component_type=Body, module_name="mod1", file_path=Path("/path1")
    )

    assert loc_head1 == loc_head2  # Same component type
    assert loc_head1 != loc_body  # Different component type


# -- PathCollector tests --


def test_collector_register_component():
    """Test registering a component."""
    collector = PathCollector()
    location = collector.register_component(Head)

    assert location.component_type is Head
    assert location.module_name == "examples.middleware.path.components.head"
    assert Head in [loc.component_type for loc in collector.components]


def test_collector_register_deduplication():
    """Test registering the same component twice doesn't duplicate."""
    collector = PathCollector()
    collector.register_component(Head)
    collector.register_component(Head)

    assert len(collector.components) == 1


def test_collector_register_multiple():
    """Test registering multiple different components."""
    collector = PathCollector()
    collector.register_component(Head)
    collector.register_component(Body)

    assert len(collector.components) == 2
    types = {loc.component_type for loc in collector.components}
    assert types == {Head, Body}


def test_collector_register_asset():
    """Test registering an asset reference."""
    collector = PathCollector()
    location = collector.register_component(Head)
    asset_ref = collector.register_asset(location, "./static/styles.css")

    assert asset_ref.relative_path == "./static/styles.css"
    assert asset_ref.module_path == PurePosixPath(
        "examples/middleware/path/components/head/static/styles.css"
    )
    assert asset_ref.component_location is location
    assert len(collector.assets) == 1


def test_collector_collect_from_link_tag():
    """Test collecting assets from link tags."""
    collector = PathCollector()
    location = collector.register_component(Head)

    node = html(t'<link rel="stylesheet" href="./static/styles.css">')
    collector.collect_from_node(node, location)

    assert len(collector.assets) == 1
    asset = next(iter(collector.assets))
    assert asset.relative_path == "./static/styles.css"


def test_collector_collect_from_script_tag():
    """Test collecting assets from script tags."""
    collector = PathCollector()
    location = collector.register_component(Head)

    node = html(t'<script src="./static/app.js"></script>')
    collector.collect_from_node(node, location)

    assert len(collector.assets) == 1
    asset = next(iter(collector.assets))
    assert asset.relative_path == "./static/app.js"


def test_collector_collect_multiple_assets():
    """Test collecting multiple assets from a node tree."""
    collector = PathCollector()
    location = collector.register_component(Head)

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
    assert paths == {"./static/styles.css", "./static/app.js"}


def test_collector_skips_external_urls():
    """Test that external URLs are skipped."""
    collector = PathCollector()
    location = collector.register_component(Head)

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

    assert len(collector.assets) == 1
    asset = next(iter(collector.assets))
    assert asset.relative_path == "./local.css"


def test_collector_skips_special_schemes():
    """Test that special URL schemes are skipped."""
    collector = PathCollector()
    location = collector.register_component(Head)

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

    assert len(collector.assets) == 1
    asset = next(iter(collector.assets))
    assert asset.relative_path == "./styles.css"


def test_collector_nested_structure():
    """Test collecting from deeply nested node structure."""
    collector = PathCollector()
    location = collector.register_component(Head)

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


def test_collector_clear():
    """Test clearing collected data."""
    collector = PathCollector()
    location = collector.register_component(Head)
    collector.register_asset(location, "./styles.css")

    assert len(collector.components) == 1
    assert len(collector.assets) == 1

    collector.clear()

    assert len(collector.components) == 0
    assert len(collector.assets) == 0


# -- Integration tests --


def test_path_example_runs():
    """Test that the path example runs successfully with all assertions."""
    from examples.middleware.path.app import main

    result = main()
    assert isinstance(result, str)
    assert "<!DOCTYPE html>" in result


def test_path_example_renders_html():
    """Test that the example renders valid HTML."""
    from examples.middleware.path.app import main

    result = main()

    assert "<!DOCTYPE html>" in result
    assert "<html>" in result
    assert "<head>" in result
    assert "<body>" in result
    assert "Hello Alice!" in result


def test_static_files_exist():
    """Test that the static asset files actually exist."""
    import importlib.resources

    head_resources = importlib.resources.files(
        "examples.middleware.path.components.head"
    )

    styles_path = head_resources / "static" / "styles.css"
    script_path = head_resources / "static" / "script.js"

    assert styles_path.is_file(), "styles.css should exist"
    assert script_path.is_file(), "script.js should exist"


# -- DI tests --


def test_path_collector_injectable():
    """Test PathCollector can be discovered and resolved via scan()."""
    from tdom_svcs.services import path

    registry = HopscotchRegistry()
    scan(registry, path)

    with HopscotchContainer(registry) as container:
        collector = container.get(PathCollector)
        assert isinstance(collector, PathCollector)
        assert len(collector.components) == 0
        assert len(collector.assets) == 0


def test_path_middleware_injectable():
    """Test PathMiddleware resolves PathCollector via Inject[PathCollector]."""
    from tdom_svcs.services import path

    registry = HopscotchRegistry()
    scan(registry, path)

    with HopscotchContainer(registry) as container:
        middleware = container.get(PathMiddleware)
        assert isinstance(middleware, PathMiddleware)
        assert isinstance(middleware.collector, PathCollector)


def test_path_middleware_uses_injected_collector():
    """Test PathMiddleware registers components on the injected collector."""
    from tdom_svcs.services import path

    registry = HopscotchRegistry()
    scan(registry, path)

    with HopscotchContainer(registry) as container:
        middleware = container.get(PathMiddleware)
        collector = container.get(PathCollector)

        props = middleware(Head, {}, container)

        assert len(collector.components) == 1
        assert "_component_location" in props


def test_path_collector_shared_instance():
    """Test PathCollector is shared across multiple gets in same container."""
    from tdom_svcs.services import path

    registry = HopscotchRegistry()
    scan(registry, path)

    with HopscotchContainer(registry) as container:
        collector1 = container.get(PathCollector)
        collector2 = container.get(PathCollector)
        middleware = container.get(PathMiddleware)

        assert collector1 is collector2
        assert middleware.collector is collector1
