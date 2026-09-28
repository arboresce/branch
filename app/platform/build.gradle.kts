import java.util.Properties

plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.kmp)
}

val nativeSettings = Properties().apply { rootProject.file("../contracts/native-settings.properties").inputStream().use { load(it) } }

kotlin {
    androidLibrary {
        namespace = "ai.arboresce.branch.platform"
        compileSdk = nativeSettings.getProperty("compileSdk").toInt()
        minSdk = nativeSettings.getProperty("minSdk").toInt()
    }
    iosArm64()
    iosSimulatorArm64()
    jvmToolchain(21)
}
