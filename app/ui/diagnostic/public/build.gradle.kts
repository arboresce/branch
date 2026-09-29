import java.util.Properties
plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.compose)
    alias(libs.plugins.android.kmp)
}
val nativeSettings = Properties().apply { rootProject.file("../contracts/native-settings.properties").inputStream().use { load(it) } }
kotlin {
    androidLibrary {
        namespace = "ai.arboresce.branch.ui"
        compileSdk = nativeSettings.getProperty("compileSdk").toInt()
        minSdk = nativeSettings.getProperty("minSdk").toInt()
        androidResources.enable = true
    }
    iosArm64()
    iosSimulatorArm64()
    jvmToolchain(21)
    sourceSets {
        commonMain.dependencies {
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.ui)
            implementation(compose.components.resources)
        }
    }
}

compose.resources {
    packageOfResClass = "ai.arboresce.branch.ui.resources"
}
