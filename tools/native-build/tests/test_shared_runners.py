import os

import pytest

from branch_native_build import mobile


def write_receipt(base, directory, target, name="TEST-suite.xml", **attrs):
    results = base / directory / "test-results" / target
    results.mkdir(parents=True, exist_ok=True)
    attributes = {"tests": "1", "skipped": "0", "failures": "0", "errors": "0"}
    attributes.update({key: str(value) for key, value in attrs.items()})
    body = "".join(f' {key}="{value}"' for key, value in attributes.items())
    receipt = results / name
    receipt.write_text(f"<testsuite{body}></testsuite>")
    return receipt


def test_declared_modules_have_common_tests():
    mobile.verify_shared_runners()


def test_every_common_test_directory_is_covered():
    declared = {directory for _, directory in mobile.SHARED_COMMON_TEST_MODULES}
    assert mobile.common_test_directories() == declared


def test_shared_targets_cover_both_platforms():
    assert mobile._SHARED_TEST_TARGETS == {
        "ios": "iosSimulatorArm64Test",
        "android": "testAndroidHostTest",
    }


def test_missing_results_are_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    with pytest.raises(ValueError, match="No executed tests"):
        mobile.verify_shared_test_execution("android")


def test_all_skipped_suite_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    for _, directory in mobile.SHARED_COMMON_TEST_MODULES:
        write_receipt(tmp_path / "gradle", directory, "testAndroidHostTest", tests=3, skipped=3)
    with pytest.raises(ValueError, match="No executed tests"):
        mobile.verify_shared_test_execution("android")


def test_failing_suite_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    for _, directory in mobile.SHARED_COMMON_TEST_MODULES:
        write_receipt(tmp_path / "gradle", directory, "testAndroidHostTest", tests=2, failures=1)
    with pytest.raises(ValueError, match="Failing tests"):
        mobile.verify_shared_test_execution("android")


def test_executed_receipts_pass(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    for _, directory in mobile.SHARED_COMMON_TEST_MODULES:
        write_receipt(tmp_path / "gradle", directory, "testAndroidHostTest", tests=2)
    mobile.verify_shared_test_execution("android")


def test_wrong_target_receipt_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    for _, directory in mobile.SHARED_COMMON_TEST_MODULES:
        write_receipt(tmp_path / "gradle", directory, "iosSimulatorArm64Test", tests=2)
    with pytest.raises(ValueError, match="No executed tests"):
        mobile.verify_shared_test_execution("android")


def test_stale_receipt_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    receipts = [
        write_receipt(tmp_path / "gradle", directory, "testAndroidHostTest", tests=2)
        for _, directory in mobile.SHARED_COMMON_TEST_MODULES
    ]
    old = 1_000_000.0
    for receipt in receipts:
        os.utime(receipt, (old, old))
    with pytest.raises(ValueError, match="Stale test receipt"):
        mobile.verify_shared_test_execution("android", since=old + 10)


def test_malformed_receipt_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    results = tmp_path / "gradle/catalog/test-results/testAndroidHostTest"
    results.mkdir(parents=True)
    (results / "TEST-suite.xml").write_text("<testsuite></testsuite>")
    with pytest.raises(ValueError, match="Malformed test receipt"):
        mobile.executed_test_counts()


def test_executed_test_counts_aggregate_by_module_and_target(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    write_receipt(tmp_path / "gradle", "catalog", "testAndroidHostTest", tests=4, skipped=1)
    counts = mobile.executed_test_counts()
    assert counts[("catalog", "testAndroidHostTest")].executed == 3
