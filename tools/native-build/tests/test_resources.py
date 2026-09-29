import pytest

from branch_native_build import mobile


def test_compose_resource_destinations_are_bounded(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    for configuration, sdk, app_name in (
        ("debug", "simulator", "Branch"),
        ("release", "simulator", "Branch"),
        ("release", "device", "Branch"),
        ("debug", "simulator", "BranchCatalog"),
    ):
        source, destination = mobile.compose_resource_paths(configuration, sdk, app_name)
        assert source.name == "composeResources"
        assert destination.parts[-2:] == ("compose-resources", "composeResources")
        assert f"{app_name}.app" in destination.parts


def test_release_and_device_destinations_use_the_selected_product(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    _, release_simulator = mobile.compose_resource_paths("release", "simulator", "Branch")
    _, release_device = mobile.compose_resource_paths("release", "device", "Branch")
    assert "Release-iphonesimulator" in release_simulator.parts
    assert "Release-iphoneos" in release_device.parts


def test_valid_resource_bundle_passes(tmp_path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "values").write_text("resource")
    destination = tmp_path / "Branch.app/compose-resources/composeResources"
    mobile.verify_compose_resources(source, destination)


def test_missing_resource_bundle_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="Missing shared Compose resource"):
        mobile.verify_compose_resources(
            tmp_path / "missing",
            tmp_path / "Branch.app/compose-resources/composeResources",
        )


def test_unbounded_destination_is_rejected(tmp_path):
    source = tmp_path / "src"
    source.mkdir()
    with pytest.raises(ValueError, match="Unbounded"):
        mobile.verify_compose_resources(source, tmp_path / "Branch.app" / "resources")
