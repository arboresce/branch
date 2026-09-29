plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.compose)
}

kotlin {
    listOf(iosArm64(), iosSimulatorArm64()).forEach {
        it.binaries.framework {
            baseName = "BranchCatalogUI"
            isStatic = true
        }
    }
    sourceSets.commonMain.dependencies {
        api(project(":catalog"))
        implementation(compose.ui)
    }
}
