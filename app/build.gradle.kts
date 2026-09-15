plugins {
    alias(libs.plugins.ktlint)
    alias(libs.plugins.kotlin.multiplatform) apply false
    alias(libs.plugins.kotlin.compose) apply false
    alias(libs.plugins.compose) apply false
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.android.kmp) apply false
}
val output =
    providers
        .environmentVariable("BRANCH_BUILD_DIR")
        .orElse(rootDir.parentFile.resolve(".build").path)
allprojects {
    if (buildFile.isFile) {
        apply(plugin = "org.jlleitschuh.gradle.ktlint")
        extensions.configure<org.jlleitschuh.gradle.ktlint.KtlintExtension> {
            version.set(rootProject.libs.versions.ktlint)
            additionalEditorconfig.set(mapOf("ktlint_function_naming_ignore_when_annotated_with" to "Composable"))
            filter {
                exclude { !it.file.toPath().startsWith(projectDir.toPath()) }
            }
        }
    }
    val moduleDirectory = if (path == ":") "root" else path.removePrefix(":").replace(":", "/")
    layout.buildDirectory.set(file(output.get()).resolve("gradle/$moduleDirectory"))
    dependencyLocking { lockAllConfigurations() }
}
