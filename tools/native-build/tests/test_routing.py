import pytest

from branch_native_build import cli, mobile, native


def test_android_release_test_rejected_before_building(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("build must not run for an unsupported test configuration")

    monkeypatch.setattr(mobile, "build", fail)
    with pytest.raises(ValueError, match="debug configuration"):
        mobile.test("android", "release")


@pytest.mark.parametrize("action", ["lint", "check-native", "build-native", "setup", "dev"])
def test_actions_reject_a_configuration_option(action):
    with pytest.raises(ValueError, match="configuration option"):
        cli.resolve(action, "ios", "release", None)


@pytest.mark.parametrize("action", ["lint", "check-native", "build-native", "setup", "dev"])
def test_actions_reject_an_sdk_option(action):
    with pytest.raises(ValueError, match="sdk option"):
        cli.resolve(action, "ios", None, "device")


def test_no_platform_actions_reject_a_platform_argument():
    with pytest.raises(ValueError, match="does not accept a platform"):
        cli.resolve("contract-check", "ios", None, None)


def test_android_build_rejects_the_device_sdk():
    with pytest.raises(ValueError, match="device sdk"):
        cli.resolve("build", "android", None, "device")


def test_ios_build_accepts_release_device_routing():
    assert cli.resolve("build", "ios", "release", "device") == ("ios", "release", "device")


def test_ios_test_rejects_the_device_sdk():
    with pytest.raises(ValueError, match="Device test execution"):
        cli.resolve("test", "ios", None, "device")


def test_build_defaults_are_stable():
    assert cli.resolve("build", "ios", None, None) == ("ios", "debug", "simulator")
    assert cli.resolve("test", "android", None, None) == ("android", "debug", "simulator")
    assert cli.resolve("test-shared", None, None, None) == (None, "debug", "simulator")


def test_host_toolchain_resolution_is_explicit():
    assert native._ndk_prebuilt_tag("darwin") == "darwin-x86_64"
    assert native._ndk_prebuilt_tag("linux") == "linux-x86_64"
    assert native._host_library_name("darwin") == "libbranch_runtime_ffi.dylib"
    assert native._host_library_name("linux") == "libbranch_runtime_ffi.so"
    with pytest.raises(ValueError, match="Unsupported Android producer host"):
        native._ndk_prebuilt_tag("win32")
    with pytest.raises(ValueError, match="Unsupported native host"):
        native._host_library_name("win32")


def test_mismatched_ndk_prebuilt_directory_is_rejected(tmp_path, monkeypatch):
    prebuilt = tmp_path / "ndk/29.0.0/toolchains/llvm/prebuilt"
    (prebuilt / "windows-x86_64/bin").mkdir(parents=True)
    monkeypatch.setattr(native, "sdk", lambda: tmp_path)
    with pytest.raises(ValueError, match="lacks a host toolchain"):
        native._ndk_toolchain("29.0.0")


def test_matching_ndk_prebuilt_directory_is_selected(tmp_path, monkeypatch):
    host = native._ndk_prebuilt_tag()
    expected = tmp_path / f"ndk/29.0.0/toolchains/llvm/prebuilt/{host}/bin"
    expected.mkdir(parents=True)
    monkeypatch.setattr(native, "sdk", lambda: tmp_path)
    assert native._ndk_toolchain("29.0.0") == expected


def test_android_linkers_use_the_resolved_ndk_toolchain(tmp_path, monkeypatch):
    host = native._ndk_prebuilt_tag()
    bindir = tmp_path / f"ndk/29.0.0/toolchains/llvm/prebuilt/{host}/bin"
    bindir.mkdir(parents=True)
    monkeypatch.setattr(native, "sdk", lambda: tmp_path)
    config = {
        "android": {
            "ndk": "29.0.0",
            "minimum_api": "28",
            "targets": ["aarch64-linux-android", "x86_64-linux-android"],
        }
    }
    linkers = native._android_linkers(config)
    assert linkers["aarch64-linux-android"] == str(bindir / "aarch64-linux-android28-clang")
    assert linkers["x86_64-linux-android"] == str(bindir / "x86_64-linux-android28-clang")
