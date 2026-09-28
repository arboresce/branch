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
        namespace = "ai.arboresce.branch.shared"
        compileSdk = nativeSettings.getProperty("compileSdk").toInt()
        minSdk = nativeSettings.getProperty("minSdk").toInt()
    }
    iosArm64()
    iosSimulatorArm64()
    jvmToolchain(21)
    sourceSets {
        commonMain.dependencies {
            api(project(":ui:diagnostic-public"))
            implementation(project(":platform"))
            implementation(project(":ui:design-system"))
            implementation(project(":ui:patterns"))
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.ui)
        }
        commonTest.dependencies { implementation(kotlin("test")) }
    }
}
