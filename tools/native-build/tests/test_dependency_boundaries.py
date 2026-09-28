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


def test_production_modules_do_not_depend_on_the_catalog():
    for path in PRODUCTION_MODULES:
        text = (config.ROOT / path).read_text()
        assert ":catalog" not in text, path


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
