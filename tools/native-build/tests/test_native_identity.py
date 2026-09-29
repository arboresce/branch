import json
import os
import shutil
from pathlib import Path

import pytest

from branch_native_build import config, native

_BUILD_ENV = (
    "CARGO_PROFILE_RELEASE_OPT_LEVEL",
    "CARGO_PROFILE_RELEASE_LTO",
    "CARGO_PROFILE_RELEASE_DEBUG",
    "CARGO_PROFILE_RELEASE_PANIC",
    "CARGO_PROFILE_DEV_OPT_LEVEL",
    "CARGO_PROFILE_DEV_DEBUG",
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
    "CARGO_TARGET_AARCH64_APPLE_DARWIN_LINKER",
    "CARGO_TARGET_AARCH64_APPLE_DARWIN_RUSTFLAGS",
    "CARGO_TARGET_AARCH64_APPLE_IOS_LINKER",
    "CARGO_TARGET_AARCH64_APPLE_IOS_RUSTFLAGS",
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
        "CARGO_PROFILE_DEV_OPT_LEVEL",
    ],
)
def test_unsupported_profile_overrides_rejected(tmp_path, monkeypatch, name):
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv(name, "true")
    with pytest.raises(ValueError, match="Unsupported build-affecting override"):
        identity("ios")


@pytest.mark.parametrize(
    "name",
    [
        "RUSTC",
        "RUSTC_WRAPPER",
        "RUSTC_WORKSPACE_WRAPPER",
    ],
)
def test_custom_compiler_and_wrapper_selectors_are_rejected(tmp_path, monkeypatch, name):
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv(name, "/bin/true")
    with pytest.raises(ValueError, match="Unsupported build-affecting override"):
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


@pytest.mark.parametrize(
    "name",
    [
        "CARGO_TARGET_AARCH64_APPLE_DARWIN_LINKER",
        "CARGO_TARGET_AARCH64_APPLE_IOS_LINKER",
    ],
)
def test_caller_target_linkers_are_rejected(tmp_path, monkeypatch, name):
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv(name, "/tmp/linker")
    with pytest.raises(ValueError, match="Unsupported build-affecting override"):
        identity("ios")


def test_host_tooling_dev_debug_unset_is_nonsemantic(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    assert "CARGO_PROFILE_DEV_DEBUG" not in os.environ
    assert identity("ios") == baseline


def test_host_tooling_dev_debug_approved_value_is_nonsemantic(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    monkeypatch.setenv("CARGO_PROFILE_DEV_DEBUG", "line-tables-only")
    assert identity("ios") == baseline


@pytest.mark.parametrize("value", ["2", "0", "none", "", "line-tables-only ", "invalid"])
def test_other_dev_debug_values_are_rejected_without_echoing_values(tmp_path, monkeypatch, value):
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv("CARGO_PROFILE_DEV_DEBUG", value)
    with pytest.raises(ValueError) as error:
        identity("ios")
    assert "CARGO_PROFILE_DEV_DEBUG" in str(error.value)
    if value:
        assert value not in str(error.value)


def test_rejected_dev_debug_cannot_reuse_a_valid_cached_cohort(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    cached = native.location("ios", baseline)
    cached.mkdir(parents=True)
    (cached / "library").write_bytes(b"native fixture")
    (cached / "manifest.json").write_text(
        json.dumps({"identity": baseline, "outputs": {"library": config.digest(b"native fixture")}})
    )
    monkeypatch.setenv("CARGO_PROFILE_DEV_DEBUG", "2")
    with pytest.raises(ValueError, match="CARGO_PROFILE_DEV_DEBUG"):
        native.check("ios")


def test_retained_host_and_target_rustflags_change_identity(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    monkeypatch.setenv("RUSTFLAGS", "-Copt-level=1")
    monkeypatch.setenv("CARGO_TARGET_AARCH64_APPLE_IOS_RUSTFLAGS", "-Cdebug-assertions=on")
    changed = identity("ios")
    overrides = changed["toolchain"]["overrides"]
    assert overrides["RUSTFLAGS"] == "-Copt-level=1"
    assert overrides["CARGO_TARGET_AARCH64_APPLE_IOS_RUSTFLAGS"] == "-Cdebug-assertions=on"
    assert native.location("ios", changed) != native.location("ios", baseline)


def test_host_target_rustflags_change_identity(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    monkeypatch.setenv("CARGO_TARGET_AARCH64_APPLE_DARWIN_RUSTFLAGS", "-Copt-level=2")
    changed = identity("ios")
    assert (
        changed["toolchain"]["overrides"]["CARGO_TARGET_AARCH64_APPLE_DARWIN_RUSTFLAGS"]
        == "-Copt-level=2"
    )
    assert native.location("ios", changed) != native.location("ios", baseline)


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
    (base / ".cargo/config.toml").write_text(
        '[target.aarch64-apple-ios]\nrustflags = ["-Copt-level=1"]\n'
    )
    identity = prepare(tmp_path, monkeypatch, root=base / "repo")
    baseline = identity("ios")
    assert baseline["toolchain"]["cargo_config"]["ancestor/1"]["target"] == {
        "aarch64-apple-ios": {"rustflags": ["-Copt-level=1"]}
    }
    (base / ".cargo/config.toml").write_text(
        '[target.aarch64-apple-ios]\nrustflags = ["-Copt-level=2"]\n'
    )
    assert native.location("ios", identity("ios")) != native.location("ios", baseline)


def test_unsupported_cargo_config_is_rejected(tmp_path, monkeypatch):
    base = tmp_path / "level"
    base.mkdir()
    (base / ".cargo").mkdir()
    (base / ".cargo/config.toml").write_text('[build]\ntarget = "x86_64-unknown-linux-gnu"\n')
    identity = prepare(tmp_path, monkeypatch, root=base / "repo")
    with pytest.raises(ValueError, match="Unsupported Cargo configuration build.target"):
        identity("ios")


def test_cargo_config_profile_is_rejected(tmp_path, monkeypatch):
    home = tmp_path / "cargo-home"
    (home / ".cargo").mkdir(parents=True)
    (home / ".cargo/config.toml").write_text("[profile.dev]\nopt-level = 1\n")
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv("CARGO_HOME", str(home / ".cargo"))
    with pytest.raises(ValueError, match="Unsupported Cargo configuration profile"):
        identity("ios")


def test_cargo_config_target_linker_is_rejected(tmp_path, monkeypatch):
    home = tmp_path / "cargo-home"
    (home / ".cargo").mkdir(parents=True)
    (home / ".cargo/config.toml").write_text('[target.aarch64-apple-ios]\nlinker = "custom"\n')
    identity = prepare(tmp_path, monkeypatch)
    monkeypatch.setenv("CARGO_HOME", str(home / ".cargo"))
    with pytest.raises(ValueError, match="Unsupported Cargo configuration target.linker"):
        identity("ios")


def test_cargo_env_table_is_rejected_without_echoing_values(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    home = tmp_path / "cargo-home"
    home.mkdir()
    marker = "synthetic-token-do-not-echo-42"
    (home / "config.toml").write_text(f'[env]\nSYNTHETIC_TOKEN = "{marker}"\n')
    monkeypatch.setenv("CARGO_HOME", str(home))
    with pytest.raises(ValueError) as error:
        identity("ios")
    assert "env" in str(error.value)
    assert marker not in str(error.value)


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


def test_output_paths_do_not_change_identity(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    monkeypatch.setenv("CARGO_TARGET_DIR", str(tmp_path / "cargo-output"))
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path / "build-output"))
    monkeypatch.setenv("BRANCH_NATIVE", str(tmp_path / "stale-cohort"))
    assert identity("ios") == baseline


def test_cargo_config_output_routing_is_not_semantic(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    home = tmp_path / "cargo-home"
    home.mkdir()
    (home / "config.toml").write_text('[build]\ntarget-dir = "somewhere-else"\n')
    monkeypatch.setenv("CARGO_HOME", str(home))
    assert identity("ios") == baseline


def test_repository_cargo_config_output_routing_is_not_semantic(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    (tmp_path / ".cargo").mkdir()
    (tmp_path / ".cargo/config.toml").write_text('[build]\ntarget-dir = "elsewhere"\n')
    assert identity("ios") == baseline


def test_ancestor_cargo_config_output_routing_is_not_semantic(tmp_path, monkeypatch):
    base = tmp_path / "level"
    base.mkdir()
    (base / ".cargo").mkdir()
    (base / ".cargo/config.toml").write_text('[build]\ntarget-dir = "elsewhere"\n')
    identity = prepare(tmp_path, monkeypatch, root=base / "repo")
    baseline = identity("ios")
    (base / ".cargo/config.toml").write_text('[build]\ntarget-dir = "other-elsewhere"\n')
    assert identity("ios") == baseline


def test_repository_semantic_cargo_config_changes_identity(tmp_path, monkeypatch):
    identity = prepare(tmp_path, monkeypatch)
    baseline = identity("ios")
    (tmp_path / ".cargo").mkdir()
    (tmp_path / ".cargo/config.toml").write_text('[build]\nrustflags = ["-Copt-level=1"]\n')
    changed = identity("ios")
    assert changed["toolchain"]["cargo_config"]["repository"]["build"] == {
        "rustflags": ["-Copt-level=1"]
    }
    assert native.location("ios", changed) != native.location("ios", baseline)


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


def android_sdk(tmp_path, monkeypatch):
    ndk = "29.0.14206865"
    host = native._ndk_prebuilt_tag()
    bindir = tmp_path / f"ndk/{ndk}/toolchains/llvm/prebuilt/{host}/bin"
    bindir.mkdir(parents=True)
    (tmp_path / f"ndk/{ndk}/source.properties").write_text("Pkg.Revision = 29.0.14206865\n")
    monkeypatch.setattr(native, "sdk", lambda: tmp_path)
    return bindir


def recording_runner(record):
    def runner(*args, env=None, **kwargs):
        record.append((args, dict(env or {})))
        if env is None:
            return
        target_dir = Path(env["CARGO_TARGET_DIR"])
        if args[:2] == ("cargo", "build"):
            if "--target" in args:
                target = args[args.index("--target") + 1]
                library = target_dir / target / "release" / "libbranch_runtime_ffi.so"
            else:
                library = target_dir / "release" / "libbranch_runtime_ffi.so"
            library.parent.mkdir(parents=True, exist_ok=True)
            library.write_bytes(b"native fixture")
        elif args[:2] == ("cargo", "run"):
            out = Path(args[args.index("--out-dir") + 1])
            out.mkdir(parents=True, exist_ok=True)
            (out / "BranchRuntimeFFI.kt").write_text("// generated\n")
            (out / "BranchRuntimeFFI.h").write_text("// generated\n")
            (out / "BranchRuntimeFFI.modulemap").write_text("// generated\n")
        elif args[:1] == ("xcodebuild",):
            output = Path(args[args.index("-output") + 1])
            output.mkdir(parents=True, exist_ok=True)
            (output / "Info.plist").write_text("fixture\n")

    return runner


def test_build_rejects_selectors_before_any_subprocess(tmp_path, monkeypatch):
    prepare(tmp_path, monkeypatch)
    record = []
    monkeypatch.setattr(native, "run", recording_runner(record))
    monkeypatch.setenv("RUSTC", "/bin/true")
    with pytest.raises(ValueError, match="Unsupported build-affecting override"):
        native.build("ios")
    assert record == []


def test_actual_android_subprocesses_receive_linkers_and_flags(tmp_path, monkeypatch):
    prepare(tmp_path, monkeypatch)
    bindir = android_sdk(tmp_path, monkeypatch)
    record = []
    monkeypatch.setattr(native, "run", recording_runner(record))
    monkeypatch.setenv("RUSTFLAGS", "-Copt-level=1")
    native.build("android")
    assert record
    linkers = {
        "CARGO_TARGET_AARCH64_LINUX_ANDROID_LINKER": str(bindir / "aarch64-linux-android28-clang"),
        "CARGO_TARGET_X86_64_LINUX_ANDROID_LINKER": str(bindir / "x86_64-linux-android28-clang"),
    }
    for args, env in record:
        if args[:2] in {("cargo", "build"), ("cargo", "run")}:
            assert env["RUSTFLAGS"] == "-Copt-level=1"
        if args[:2] == ("cargo", "build"):
            for key, value in linkers.items():
                assert env[key] == value


def test_actual_ios_subprocesses_share_the_resolved_policy(tmp_path, monkeypatch):
    prepare(tmp_path, monkeypatch)
    record = []
    monkeypatch.setattr(native, "run", recording_runner(record))
    monkeypatch.setenv("CARGO_TARGET_AARCH64_APPLE_IOS_RUSTFLAGS", "-Cdebug-assertions=on")
    native.build("ios")
    assert record
    saw_target = False
    for args, env in record:
        if args[:2] == ("cargo", "build") and "--target" in args:
            saw_target = True
            assert env["CARGO_TARGET_AARCH64_APPLE_IOS_RUSTFLAGS"] == "-Cdebug-assertions=on"
        assert "CARGO_TARGET_AARCH64_APPLE_DARWIN_LINKER" not in env
    assert saw_target


def test_build_rejects_other_dev_debug_before_any_subprocess(tmp_path, monkeypatch):
    prepare(tmp_path, monkeypatch)
    record = []
    monkeypatch.setattr(native, "run", recording_runner(record))
    monkeypatch.setenv("CARGO_PROFILE_DEV_DEBUG", "2")
    with pytest.raises(ValueError, match="CARGO_PROFILE_DEV_DEBUG"):
        native.build("ios")
    assert record == []


def test_actual_subprocesses_omit_an_unset_dev_debug(tmp_path, monkeypatch):
    prepare(tmp_path, monkeypatch)
    record = []
    monkeypatch.setattr(native, "run", recording_runner(record))
    native.build("ios")
    cargo_envs = [env for args, env in record if args[:2] in {("cargo", "build"), ("cargo", "run")}]
    assert cargo_envs
    assert all("CARGO_PROFILE_DEV_DEBUG" not in env for env in cargo_envs)


def test_actual_subprocesses_forward_the_approved_dev_debug(tmp_path, monkeypatch):
    prepare(tmp_path, monkeypatch)
    monkeypatch.setenv("CARGO_PROFILE_DEV_DEBUG", "line-tables-only")
    record = []
    monkeypatch.setattr(native, "run", recording_runner(record))
    native.build("ios")
    cargo_envs = [env for args, env in record if args[:2] in {("cargo", "build"), ("cargo", "run")}]
    assert cargo_envs
    assert all(env["CARGO_PROFILE_DEV_DEBUG"] == "line-tables-only" for env in cargo_envs)
