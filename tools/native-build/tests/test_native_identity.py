import json
import shutil

import pytest

from branch_native_build import config, native

_BUILD_ENV = (
    "CARGO_PROFILE_RELEASE_OPT_LEVEL",
    "CARGO_PROFILE_RELEASE_LTO",
    "CARGO_PROFILE_RELEASE_DEBUG",
    "CARGO_PROFILE_RELEASE_PANIC",
    "CARGO_BUILD_RUSTC",
    "CARGO_BUILD_RUSTC_WRAPPER",
    "CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER",
    "CARGO_BUILD_TARGET",
    "CARGO_INCREMENTAL",
    "IPHONEOS_DEPLOYMENT_TARGET",
    "RUSTFLAGS",
    "CARGO_ENCODED_RUSTFLAGS",
    "CARGO_BUILD_RUSTFLAGS",
    "RUSTC",
    "RUSTC_WRAPPER",
    "RUSTC_WORKSPACE_WRAPPER",
)


def native_root(target):
    target.mkdir(parents=True, exist_ok=True)
    for name in ("Cargo.toml", "Cargo.lock", "rust-toolchain.toml"):
        shutil.copyfile(config.ROOT / name, target / name)
    for directory in ("core", "app/rust", "contracts", "tools"):
        shutil.copytree(config.ROOT / directory, target / directory)
    return target


def fake_capture(*args):
    if args[0] == "rustc":
        return "rustc 1.98.0 (fixture)"
    if args[0] == "xcodebuild":
        return "Xcode 26.6"
    if args[0] == "xcrun":
        return "26.5"
    raise AssertionError(args)


def prepare(tmp_path, monkeypatch, root=None):
    root = native_root(root or tmp_path)
    monkeypatch.setattr(native, "ROOT", root)
    monkeypatch.setattr(native, "capture", fake_capture)
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path / "build"))
    monkeypatch.setenv("CARGO_HOME", str(tmp_path / "cargo-home"))
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
    wrapper = tmp_path / "fake-wrapper"
    wrapper.write_text("#!/bin/sh\nexit 0\n")
    wrapper.chmod(0o755)
    monkeypatch.setenv("RUSTC_WRAPPER", str(wrapper))
    changed = identity("ios")
    assert changed["toolchain"]["overrides"]["RUSTC_WRAPPER"] == str(wrapper.resolve())
    assert native.location("ios", changed) != native.location("ios", baseline)


def test_compiler_selection_resolves_the_real_executable(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    real = tmp_path / "rustc-real"
    real.write_text("#!/bin/sh\nexit 0\n")
    real.chmod(0o755)
    link = tmp_path / "rustc-link"
    link.symlink_to(real)
    monkeypatch.setenv("RUSTC", str(link))
    changed = identity("ios")
    assert changed["toolchain"]["overrides"]["RUSTC"] == str(real.resolve())


def test_unresolved_tool_selection_is_rejected(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv("RUSTC_WRAPPER", "definitely-not-an-installed-tool")
    with pytest.raises(ValueError, match="Unresolved build tool RUSTC_WRAPPER"):
        identity("ios")


@pytest.mark.parametrize(
    "name",
    [
        "CARGO_BUILD_RUSTC",
        "CARGO_BUILD_RUSTC_WRAPPER",
        "CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER",
        "CARGO_BUILD_TARGET",
        "CARGO_INCREMENTAL",
    ],
)
def test_unsupported_cargo_aliases_are_rejected(tmp_path, monkeypatch, name):
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv(name, "override")
    with pytest.raises(ValueError, match="Unsupported build-affecting override"):
        identity("ios")


def test_cargo_home_semantic_config_changes_identity(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    home = tmp_path / "cargo-home"
    home.mkdir()
    (home / "config.toml").write_text('[build]\nrustflags = ["-Copt-level=1"]\n')
    monkeypatch.setenv("CARGO_HOME", str(home))
    changed = identity("ios")
    recorded = changed["toolchain"]["cargo_config"]["cargo-home"]["build"]
    assert recorded["rustflags"] == ["-Copt-level=1"]
    assert native.location("ios", changed) != native.location("ios", baseline)


def test_ancestor_semantic_config_changes_identity(tmp_path, monkeypatch):
    base = tmp_path / "level"
    base.mkdir()
    (base / ".cargo").mkdir()
    (base / ".cargo/config.toml").write_text('[target.aarch64-apple-ios]\nlinker = "ancestor"\n')
    identity = prepare(tmp_path, monkeypatch, root=base / "repo")
    baseline = identity("ios")
    assert baseline["toolchain"]["cargo_config"]["ancestor/1"]["target"] == {
        "aarch64-apple-ios": {"linker": "ancestor"}
    }
    (base / ".cargo/config.toml").write_text('[target.aarch64-apple-ios]\nlinker = "changed"\n')
    assert native.location("ios", identity("ios")) != native.location("ios", baseline)


def test_unsupported_cargo_config_is_rejected(tmp_path, monkeypatch):
    base = tmp_path / "level"
    base.mkdir()
    (base / ".cargo").mkdir()
    (base / ".cargo/config.toml").write_text('[build]\ntarget = "x86_64-unknown-linux-gnu"\n')
    identity = prepare(tmp_path, monkeypatch, root=base / "repo")
    with pytest.raises(ValueError, match="Unsupported Cargo configuration build.target"):
        identity("ios")


def test_cargo_home_credentials_are_not_hashed(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    home = tmp_path / "cargo-home"
    home.mkdir()
    (home / "config.toml").write_text(
        '[registries.crates-io]\nprotocol = "sparse"\n[net]\ngit-fetch-with-cli = true\n'
    )
    monkeypatch.setenv("CARGO_HOME", str(home))
    assert identity("ios") == baseline


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
