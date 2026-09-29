import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}

val nativeSettings = Properties().apply { rootProject.file("../contracts/native-settings.properties").inputStream().use { load(it) } }

android {
    namespace = "ai.arboresce.branch.catalog.host"
    compileSdk = nativeSettings.getProperty("compileSdk").toInt()
    defaultConfig {
        applicationId = "ai.arboresce.branch.catalog"
        minSdk = nativeSettings.getProperty("minSdk").toInt()
        targetSdk = nativeSettings.getProperty("targetSdk").toInt()
        versionCode = nativeSettings.getProperty("versionCode").toInt()
        versionName = nativeSettings.getProperty("versionName")
        resValue("string", "app_name", "Branch Catalog")
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }
    buildFeatures {
        compose = true
        resValues = true
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_21
        targetCompatibility = JavaVersion.VERSION_21
    }
    packaging { resources.excludes += "/META-INF/{AL2.0,LGPL2.1}" }
}

dependencies {
    implementation(project(":catalog"))
    implementation(project(":shared:app"))
    implementation(libs.activity.compose)
    implementation(libs.lifecycle.runtime.compose)
    implementation(libs.coroutines.android)
    androidTestImplementation("androidx.test.ext:junit:1.3.0")
    androidTestImplementation("androidx.test:runner:1.7.0")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.10.5")
    debugImplementation("androidx.compose.ui:ui-test-manifest:1.10.5")
}
