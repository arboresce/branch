import os
import subprocess

import pytest

from branch_native_build import config, mobile

INSTALLER = config.ROOT / "scripts/install-compose-resources.sh"


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


def test_resource_bundle_without_regular_files_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    source = make_source(tmp_path, empty=True)
    (source / "nested").mkdir()
    with pytest.raises(ValueError, match="Empty shared Compose resource"):
        mobile.verify_compose_resources(source, app_product(tmp_path))


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


def test_intermediate_destination_symlink_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    source = make_source(tmp_path)
    product = app_product(tmp_path)
    outside = tmp_path / "outside"
    (outside / "composeResources").mkdir(parents=True)
    product.mkdir(parents=True)
    (product / "compose-resources").symlink_to(outside)
    with pytest.raises(ValueError, match="symlink"):
        mobile.verify_compose_resources(source, product)


def test_symlinked_source_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    real = make_source(tmp_path)
    link = tmp_path / "link-composeResources"
    link.symlink_to(real)
    with pytest.raises(ValueError, match="Missing shared Compose resource"):
        mobile.verify_compose_resources(link, app_product(tmp_path))


def test_symlinked_source_tree_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    source = make_source(tmp_path)
    (source / "linked").symlink_to(source / "value")
    with pytest.raises(ValueError, match="Symlinked shared Compose resource"):
        mobile.verify_compose_resources(source, app_product(tmp_path))


def run_installer(source, build_dir, app_name="Branch"):
    env = dict(os.environ)
    env["TARGET_BUILD_DIR"] = str(build_dir)
    env["WRAPPER_NAME"] = f"{app_name}.app"
    env["BRANCH_COMPOSE_RESOURCES"] = str(source)
    env["BRANCH_COMPOSE_BUNDLE"] = str(
        build_dir / f"{app_name}.app/compose-resources/composeResources"
    )
    return subprocess.run(
        ["bash", str(INSTALLER)], env=env, capture_output=True, text=True, check=False
    )


def test_actual_installer_copies_valid_resources(tmp_path):
    source = make_source(tmp_path)
    build_dir = tmp_path / "products"
    (build_dir / "Branch.app").mkdir(parents=True)
    result = run_installer(source, build_dir)
    assert result.returncode == 0, result.stderr
    copied = build_dir / "Branch.app/compose-resources/composeResources/value"
    assert copied.read_text() == "resource"


def test_actual_installer_rejects_intermediate_symlink_and_preserves_sentinel(tmp_path):
    source = make_source(tmp_path)
    build_dir = tmp_path / "products"
    app = build_dir / "Branch.app"
    app.mkdir(parents=True)
    outside = tmp_path / "outside"
    (outside / "composeResources").mkdir(parents=True)
    sentinel = outside / "composeResources/sentinel.txt"
    sentinel.write_text("keep")
    (app / "compose-resources").symlink_to(outside)
    result = run_installer(source, build_dir)
    assert result.returncode != 0
    assert sentinel.read_text() == "keep"


def test_actual_installer_rejects_empty_source_and_preserves_sentinel(tmp_path):
    source = make_source(tmp_path, empty=True)
    build_dir = tmp_path / "products"
    app = build_dir / "Branch.app"
    app.mkdir(parents=True)
    sentinel = app / "sentinel.txt"
    sentinel.write_text("keep")
    result = run_installer(source, build_dir)
    assert result.returncode != 0
    assert sentinel.read_text() == "keep"


def test_actual_installer_rejects_symlinked_source(tmp_path):
    real = make_source(tmp_path)
    link = tmp_path / "link-composeResources"
    link.symlink_to(real)
    build_dir = tmp_path / "products"
    (build_dir / "Branch.app").mkdir(parents=True)
    result = run_installer(link, build_dir)
    assert result.returncode != 0
