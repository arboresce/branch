import json
import shutil

import pytest

from branch_native_build import config, native

_BUILD_ENV = (
    "CARGO_PROFILE_RELEASE_OPT_LEVEL",
    "CARGO_PROFILE_RELEASE_LTO",
    "CARGO_PROFILE_RELEASE_DEBUG",
    "CARGO_PROFILE_RELEASE_PANIC",
    "IPHONEOS_DEPLOYMENT_TARGET",
    "RUSTFLAGS",
    "CARGO_ENCODED_RUSTFLAGS",
    "CARGO_BUILD_RUSTFLAGS",
    "RUSTC",
    "RUSTC_WRAPPER",
    "RUSTC_WORKSPACE_WRAPPER",
)


def native_root(tmp_path):
    for name in ("Cargo.toml", "Cargo.lock", "rust-toolchain.toml"):
        shutil.copyfile(config.ROOT / name, tmp_path / name)
    for directory in ("core", "app/rust", "contracts", "tools"):
        shutil.copytree(config.ROOT / directory, tmp_path / directory)
    return tmp_path


def fake_capture(*args):
    if args[0] == "rustc":
        return "rustc 1.98.0 (fixture)"
    if args[0] == "xcodebuild":
        return "Xcode 26.6"
    if args[0] == "xcrun":
        return "26.5"
    raise AssertionError(args)


def prepare(tmp_path, monkeypatch):
    monkeypatch.setattr(native, "ROOT", native_root(tmp_path))
    monkeypatch.setattr(native, "capture", fake_capture)
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path / "build"))
    for name in _BUILD_ENV:
        monkeypatch.delenv(name, raising=False)
    return native.identity


def test_identity_records_effective_release_configuration(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    assert baseline["schema_version"] == 2
    assert baseline["toolchain"]["opt_level"] == "3"
    assert baseline["toolchain"]["deployment_target"] == "18.0"
    monkeypatch.setenv("CARGO_PROFILE_RELEASE_OPT_LEVEL", "s")
    changed = identity("ios")
    assert changed["toolchain"]["opt_level"] == "s"
    assert native.location("ios", changed) != native.location("ios", baseline)


def test_equivalent_release_inputs_are_stable(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    monkeypatch.setenv("CARGO_PROFILE_RELEASE_OPT_LEVEL", "3")
    monkeypatch.setenv("IPHONEOS_DEPLOYMENT_TARGET", "18")
    assert identity("ios") == baseline


def test_unsupported_release_opt_level_rejected(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv("CARGO_PROFILE_RELEASE_OPT_LEVEL", "fast")
    with pytest.raises(ValueError, match="CARGO_PROFILE_RELEASE_OPT_LEVEL"):
        identity("ios")


def test_deployment_target_conflict_rejected(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv("IPHONEOS_DEPLOYMENT_TARGET", "17.0")
    with pytest.raises(ValueError, match="IPHONEOS_DEPLOYMENT_TARGET"):
        identity("ios")


def test_invalid_deployment_target_rejected(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv("IPHONEOS_DEPLOYMENT_TARGET", "eighteen")
    with pytest.raises(ValueError, match="Invalid version"):
        identity("ios")


@pytest.mark.parametrize(
    "name",
    [
        "CARGO_PROFILE_RELEASE_LTO",
        "CARGO_PROFILE_RELEASE_DEBUG",
        "CARGO_PROFILE_RELEASE_PANIC",
    ],
)
def test_unsupported_release_profile_overrides_rejected(tmp_path, monkeypatch, name):
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv(name, "true")
    with pytest.raises(ValueError, match="Unsupported build-affecting override"):
        identity("ios")


def test_recorded_compiler_and_wrapper_inputs_change_identity(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    assert "RUSTC_WRAPPER" not in baseline["toolchain"]["overrides"]
    monkeypatch.setenv("RUSTC_WRAPPER", "sccache")
    changed = identity("ios")
    assert changed["toolchain"]["overrides"]["RUSTC_WRAPPER"] == "sccache"
    assert native.location("ios", changed) != native.location("ios", baseline)


def test_target_linker_input_changes_identity(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    monkeypatch.setenv("CARGO_TARGET_AARCH64_APPLE_IOS_LINKER", "/tmp/linker")
    changed = identity("ios")
    overrides = changed["toolchain"]["overrides"]
    assert overrides["CARGO_TARGET_AARCH64_APPLE_IOS_LINKER"] == "/tmp/linker"
    assert native.location("ios", changed) != native.location("ios", baseline)


def test_output_paths_do_not_change_identity(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    monkeypatch.setenv("CARGO_TARGET_DIR", str(tmp_path / "cargo-output"))
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path / "build-output"))
    monkeypatch.setenv("BRANCH_NATIVE", str(tmp_path / "stale-cohort"))
    assert identity("ios") == baseline


def test_changed_profile_cannot_reuse_a_stale_cohort(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    stale = native.location("ios", baseline)
    stale.mkdir(parents=True)
    (stale / "library").write_bytes(b"native fixture")
    (stale / "manifest.json").write_text(
        json.dumps(
            {
                "identity": baseline,
                "outputs": {"library": config.digest(b"native fixture")},
            }
        )
    )
    monkeypatch.setenv("CARGO_PROFILE_RELEASE_OPT_LEVEL", "2")
    changed = identity("ios")
    assert native.location("ios", changed) != stale
    with pytest.raises(ValueError, match="integrity"):
        native.verify(stale, changed)
