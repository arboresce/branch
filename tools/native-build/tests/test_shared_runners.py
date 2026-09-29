import pytest

from branch_native_build import mobile


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


def test_missing_results_are_rejected():
    with pytest.raises(ValueError, match="No executed tests"):
        mobile.verify_shared_test_execution("android", {})


def test_executed_test_counts_aggregate_by_module_and_target(tmp_path, monkeypatch):
    monkeypatch.setenv("BRANCH_BUILD_DIR", str(tmp_path))
    results = tmp_path / "gradle/catalog/test-results/testAndroidHostTest"
    results.mkdir(parents=True)
    (results / "TEST-catalog.xml").write_text(
        '<testsuite tests="4" failures="0" errors="0" skipped="0"></testsuite>'
    )
    counts = mobile.executed_test_counts()
    assert counts[("catalog", "testAndroidHostTest")] == 4
