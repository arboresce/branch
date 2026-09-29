from branch_native_build import config

WORKFLOW = config.ROOT / ".github/workflows/branch-checks.yml"
MAKEFILE = config.ROOT / "Makefile"


def test_ci_uses_linux_android_and_arm64_apple_runners():
    text = WORKFLOW.read_text()
    assert "runs-on: ubuntu-latest" in text
    assert "runs-on: macos-15" in text
    assert 'java-version: "21"' in text
    assert "android-actions/setup-android" in text
    assert "ReactiveCircus/android-emulator-runner" in text


def test_ci_selects_one_python_environment_and_explicit_emulator():
    text = WORKFLOW.read_text()
    assert "UV_PROJECT_ENVIRONMENT" in text
    assert text.count("UV_PROJECT_ENVIRONMENT") == 1
    assert "ANDROID_SERIAL" in text
    assert "xcodebuild -version" in text


def test_ci_commands_are_real_make_targets():
    workflow = WORKFLOW.read_text()
    makefile = MAKEFILE.read_text()
    for target in (
        "verify-rust",
        "check-tools",
        "setup-android",
        "check-android",
        "test-shared-android",
        "test-android",
        "test-catalog-android",
        "setup-ios",
        "check-ios",
        "test-shared-ios",
        "test-ios",
        "test-catalog-ios",
    ):
        assert f"make {target}" in workflow, target
        assert target in makefile, target
