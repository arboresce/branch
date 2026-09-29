import pytest

from branch_native_build import mobile


def test_source_aggregation_is_consumer_specific(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    shared = mobile.compose_resource_source("shared/xc-framework", "simulator")
    catalog = mobile.compose_resource_source("catalog/xc-framework", "simulator")
    assert "shared/xc-framework" in str(shared)
    assert "catalog/xc-framework" in str(catalog)
    assert shared != catalog


def test_destinations_are_the_selected_app_descendant(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    for configuration, sdk, app_name, module in (
        ("debug", "simulator", "Branch", "shared/xc-framework"),
        ("release", "simulator", "Branch", "shared/xc-framework"),
        ("release", "device", "Branch", "shared/xc-framework"),
        ("debug", "simulator", "BranchCatalog", "catalog/xc-framework"),
        ("release", "device", "BranchCatalog", "catalog/xc-framework"),
    ):
        source, destination = mobile.compose_resource_paths(configuration, sdk, app_name, module)
        product = mobile.ios_app_product(configuration, sdk, app_name)
        assert destination == product / "compose-resources" / "composeResources"
        assert destination.parts[-2:] == ("compose-resources", "composeResources")
        assert source.name == "composeResources"


def test_release_and_device_destinations_use_the_selected_product(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    _, release_simulator = mobile.compose_resource_paths(
        "release", "simulator", "Branch", "shared/xc-framework"
    )
    _, release_device = mobile.compose_resource_paths(
        "release", "device", "Branch", "shared/xc-framework"
    )
    assert "Release-iphonesimulator" in release_simulator.parts
    assert "Release-iphoneos" in release_device.parts


def make_source(tmp_path, empty=False):
    source = tmp_path / "aggregated/composeResources"
    source.mkdir(parents=True)
    if not empty:
        (source / "value").write_text("resource")
    return source


def app_product(tmp_path, name="Branch"):
    return tmp_path / "ios/derived/Build/Products/Debug-iphonesimulator" / f"{name}.app"


def test_valid_resource_bundle_passes(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    source = make_source(tmp_path)
    destination = mobile.verify_compose_resources(source, app_product(tmp_path))
    assert destination == app_product(tmp_path) / "compose-resources" / "composeResources"


def test_missing_resource_bundle_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    with pytest.raises(ValueError, match="Missing shared Compose resource"):
        mobile.verify_compose_resources(tmp_path / "missing", app_product(tmp_path))


def test_empty_resource_bundle_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    with pytest.raises(ValueError, match="Empty shared Compose resource"):
        mobile.verify_compose_resources(make_source(tmp_path, empty=True), app_product(tmp_path))


def test_destination_outside_the_built_products_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    source = make_source(tmp_path)
    outside = tmp_path / "Elsewhere.app"
    with pytest.raises(ValueError, match="escapes built products"):
        mobile.verify_compose_resources(source, outside)


def test_non_app_product_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    source = make_source(tmp_path)
    not_an_app = tmp_path / "ios/derived/Build/Products/Debug-iphonesimulator/Branch"
    with pytest.raises(ValueError, match="Unbounded"):
        mobile.verify_compose_resources(source, not_an_app)


def test_symlinked_destination_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    source = make_source(tmp_path)
    product = app_product(tmp_path)
    (product / "compose-resources").mkdir(parents=True)
    (product / "compose-resources" / "composeResources").symlink_to(source)
    with pytest.raises(ValueError, match="symlink"):
        mobile.verify_compose_resources(source, product)


def test_symlinked_source_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    real = make_source(tmp_path)
    link = tmp_path / "link-composeResources"
    link.symlink_to(real)
    with pytest.raises(ValueError, match="Missing shared Compose resource"):
        mobile.verify_compose_resources(link, app_product(tmp_path))
