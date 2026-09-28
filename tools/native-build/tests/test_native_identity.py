import shutil

import pytest

from branch_native_build import config, native


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
    monkeypatch.delenv("CARGO_PROFILE_RELEASE_OPT_LEVEL", raising=False)
    monkeypatch.delenv("IPHONEOS_DEPLOYMENT_TARGET", raising=False)
    monkeypatch.delenv("RUSTFLAGS", raising=False)
    monkeypatch.delenv("CARGO_ENCODED_RUSTFLAGS", raising=False)
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
