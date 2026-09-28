plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.compose)
}
kotlin {
    listOf(iosArm64(), iosSimulatorArm64()).forEach {
        it.binaries.framework {
            baseName = "BranchUI"
            isStatic = true
        }
    }
    sourceSets.commonMain.dependencies {
        api(project(":shared:app"))
        implementation(project(":ui:diagnostic-public"))
        implementation(compose.ui)
    }
}
