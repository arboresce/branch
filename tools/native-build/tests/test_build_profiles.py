from branch_native_build import mobile


def test_release_simulator_framework_and_configuration():
    env = mobile.apple_environment({}, "release", "simulator")
    assert env["BRANCH_IOS_CONFIGURATION"] == "Release"
    assert env["BRANCH_UI"].endswith("bin/iosSimulatorArm64/releaseFramework/BranchUI.framework")


def test_debug_simulator_framework_and_configuration():
    env = mobile.apple_environment({}, "debug", "simulator")
    assert env["BRANCH_IOS_CONFIGURATION"] == "Debug"
    assert env["BRANCH_UI"].endswith("bin/iosSimulatorArm64/debugFramework/BranchUI.framework")


def test_device_framework_uses_arm64_architecture():
    env = mobile.apple_environment({}, "release", "device")
    assert env["BRANCH_UI"].endswith("bin/iosArm64/releaseFramework/BranchUI.framework")
