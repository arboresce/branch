from branch_native_build import config

PRODUCTION_MODULES = (
    "app/android/app/build.gradle.kts",
    "app/shared/app/build.gradle.kts",
    "app/shared/xc-framework/build.gradle.kts",
    "app/platform/build.gradle.kts",
    "app/ui/design-system/build.gradle.kts",
    "app/ui/diagnostic/public/build.gradle.kts",
    "app/ui/patterns/build.gradle.kts",
)
CATALOG_MODULES = (
    "app/catalog/build.gradle.kts",
    "app/catalog/android/build.gradle.kts",
    "app/catalog/xc-framework/build.gradle.kts",
)


def test_production_modules_do_not_depend_on_the_catalog():
    for path in PRODUCTION_MODULES:
        text = (config.ROOT / path).read_text()
        assert ":catalog" not in text, path


def test_catalog_modules_are_separate_consumers():
    android = (config.ROOT / "app/catalog/android/build.gradle.kts").read_text()
    assert 'applicationId = "ai.arboresce.branch.catalog"' in android
    assert 'project(":catalog")' in android
    bridge = (config.ROOT / "app/catalog/xc-framework/build.gradle.kts").read_text()
    assert 'project(":catalog")' in bridge


def test_production_android_identity_is_unchanged():
    text = (config.ROOT / "contracts/application.toml").read_text()
    assert 'bundle_id = "ai.arboresce.branch"' in text
    settings = (config.ROOT / "contracts/native-settings.properties").read_text()
    assert "applicationId=ai.arboresce.branch\n" in settings


def test_catalog_consumes_shared_modules():
    text = (config.ROOT / "app/catalog/build.gradle.kts").read_text()
    for dependency in (
        'project(":platform")',
        'project(":shared:app")',
        'project(":ui:design-system")',
        'project(":ui:patterns")',
    ):
        assert dependency in text


def test_catalog_fixture_identifiers_are_namespaced():
    text = (
        config.ROOT
        / "app/catalog/src/commonMain/kotlin/ai/arboresce/branch/catalog/CatalogFixtures.kt"
    ).read_text()
    assert '"catalog-' in text
