import java.util.Properties
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
}
val nativeSettings = Properties().apply { rootProject.file("../contracts/native-settings.properties").inputStream().use { load(it) } }
val nativeRoot = providers.environmentVariable("BRANCH_NATIVE").orElse("/unprepared-branch-native")
android {
    namespace = "ai.arboresce.branch"
    compileSdk = nativeSettings.getProperty("compileSdk").toInt()
    ndkVersion = nativeSettings.getProperty("ndkVersion")
    defaultConfig {
        applicationId = nativeSettings.getProperty("applicationId")
        minSdk = nativeSettings.getProperty("minSdk").toInt()
        targetSdk = nativeSettings.getProperty("targetSdk").toInt()
        versionCode = nativeSettings.getProperty("versionCode").toInt()
        versionName = nativeSettings.getProperty("versionName")
        resValue("string", "app_name", nativeSettings.getProperty("displayName"))
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        ndk { abiFilters += nativeSettings.getProperty("abis").split(",") }
    }
    buildFeatures {
        compose = true
        resValues = true
    }
    sourceSets.getByName("main") {
        kotlin.directories += nativeRoot.get() + "/bindings"
        jniLibs.directories += nativeRoot.get() + "/jniLibs"
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_21
        targetCompatibility = JavaVersion.VERSION_21
    }
    packaging { resources.excludes += "/META-INF/{AL2.0,LGPL2.1}" }
}
dependencies {
    implementation(project(":ui:diagnostic-public"))
    implementation(libs.activity.compose)
    implementation(libs.lifecycle.runtime.compose)
    implementation(libs.lifecycle.viewmodel.compose)
    implementation(libs.coroutines.android)
    implementation("net.java.dev.jna:jna:${libs.versions.jna.get()}@aar")
    androidTestImplementation("androidx.test.ext:junit:1.3.0")
    androidTestImplementation("androidx.test:runner:1.7.0")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.10.5")
    debugImplementation("androidx.compose.ui:ui-test-manifest:1.10.5")
}
val verifyNative by tasks.registering(Exec::class) {
    workingDir(rootProject.projectDir.parentFile)
    commandLine("bash", "scripts/commands.sh", "check-native-android")
}
tasks.named("preBuild") { dependsOn(verifyNative) }
