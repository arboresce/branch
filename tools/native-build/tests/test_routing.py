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
