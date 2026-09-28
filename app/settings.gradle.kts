pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "branch-by-arboresce"

fun module(
    directoryPath: String,
    projectPath: String,
) {
    val directory = file(directoryPath)
    require(directory.isDirectory) { "Missing module directory: $directoryPath" }
    require(findProject(projectPath) == null) { "Duplicate module identity: $projectPath" }
    include(projectPath)
    project(projectPath).projectDir = directory
}
module("android/app", ":android:app")
module("catalog", ":catalog")
module("platform", ":platform")
module("shared/app", ":shared:app")
module("shared/xc-framework", ":shared:xc-framework")
module("ui/design-system", ":ui:design-system")
module("ui/diagnostic/public", ":ui:diagnostic-public")
module("ui/patterns", ":ui:patterns")
