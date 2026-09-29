import re

import pytest

from branch_native_build import config

WORKFLOW = config.ROOT / ".github/workflows/branch-checks.yml"
MAKEFILE = config.ROOT / "Makefile"

_JOB = re.compile(r"^  ([A-Za-z0-9_-]+):\s*$")


def job_blocks(text):
    blocks = {}
    current = None
    in_jobs = False
    for line in text.splitlines():
        if line.rstrip() == "jobs:":
            in_jobs = True
            continue
        if not in_jobs:
            continue
        match = _JOB.match(line)
        if match:
            current = match.group(1)
            blocks[current] = []
        elif current is not None:
            blocks[current].append(line)
    return {name: "\n".join(lines) for name, lines in blocks.items()}


def drop_in_job(text, job, substring):
    lines = text.splitlines()
    result = []
    current = None
    in_jobs = False
    for line in lines:
        if line.rstrip() == "jobs:":
            in_jobs = True
            result.append(line)
            continue
        match = _JOB.match(line) if in_jobs else None
        if match:
            current = match.group(1)
        if in_jobs and current == job and substring in line:
            continue
        result.append(line)
    return "\n".join(result) + "\n"


def validate(text):
    blocks = job_blocks(text)
    for job in ("rust", "tools", "android", "apple"):
        assert job in blocks, f"missing CI job: {job}"

    rust = blocks["rust"]
    assert "runs-on: ubuntu-latest" in rust
    assert "make verify-rust" in rust

    tools = blocks["tools"]
    assert "setup-uv" in tools
    assert "make check-tools" in tools

    android = blocks["android"]
    assert "runs-on: ubuntu-latest" in android
    assert 'java-version: "21"' in android
    assert "setup-android" in android
    assert "setup-uv" in android
    assert "Install Android SDK prerequisites" in android
    assert "make setup-android" in android
    assert "make check-android" in android
    assert "make test-shared-android" in android
    assert "android-emulator-runner" in android
    assert "api-level: 36" in android
    assert "adb wait-for-device" in android
    assert "ANDROID_SERIAL" in android
    assert "exactly one ready emulator" in android
    assert "make test-android" in android
    assert "make test-catalog-android" in android

    apple = blocks["apple"]
    assert "runs-on: macos-26" in apple
    assert "Xcode_26.6.app" in apple
    assert "xcode-select -s" in apple
    assert "iOS 26.5" in apple
    assert "simctl list runtimes" in apple
    assert 'java-version: "21"' in apple
    assert "setup-android" in apple
    assert "setup-uv" in apple
    assert "make setup-ios" in apple
    assert "make check-ios" in apple
    assert "make test-shared-ios" in apple
    assert "make test-ios" in apple
    assert "make test-catalog-ios" in apple

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
        assert f"make {target}" in text, target
        assert target in makefile, target


def test_workflow_satisfies_every_job_prerequisite():
    validate(WORKFLOW.read_text())


@pytest.mark.parametrize(
    ("job", "removed"),
    [
        ("apple", "macos-26"),
        ("apple", "Xcode_26.6.app"),
        ("apple", "iOS 26.5"),
        ("apple", 'java-version: "21"'),
        ("apple", "setup-android"),
        ("android", 'java-version: "21"'),
        ("android", "android-emulator-runner"),
        ("android", "exactly one ready emulator"),
        ("tools", "setup-uv"),
    ],
)
def test_clean_environment_missing_prerequisite_is_rejected(job, removed):
    mutated = drop_in_job(WORKFLOW.read_text(), job, removed)
    with pytest.raises(AssertionError):
        validate(mutated)
