import contextlib
import json
import os
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from . import native
from .config import ROOT, configure, contracts, output


def toolchain_environment() -> dict:
    env = dict(os.environ, BRANCH_ROOT=str(ROOT), BRANCH_BUILD_DIR=str(output()))
    if not env.get("JAVA_HOME"):
        if sys.platform != "darwin":
            raise ValueError("Set JAVA_HOME to a JDK 21 installation")
        env["JAVA_HOME"] = native.capture("/usr/libexec/java_home", "-v", "21")
    return env


def environment(platform: str, build_native: bool = True) -> dict:
    env = toolchain_environment()
    path = native.build(platform) if build_native else native.check(platform)
    env["BRANCH_NATIVE"] = str(path)
    if platform == "android":
        env["ANDROID_HOME"] = str(native.sdk())
    return env


def cmdline_tool(name: str) -> str:
    root = native.sdk() / "cmdline-tools"
    candidates = sorted(
        entry / "bin" / name for entry in root.glob("*") if (entry / "bin" / name).is_file()
    )
    if not candidates:
        raise ValueError(f"Android command-line tool not found: {name}; install cmdline-tools")
    return str(candidates[-1])


def gradle(env: dict, *tasks: str) -> None:
    native.run(
        "bash",
        "app/gradlew",
        "-p",
        "app",
        "--no-daemon",
        "--project-cache-dir",
        str(output() / "gradle-cache"),
        f"-Pkotlin.project.persistent.dir={output() / 'kotlin-state'}",
        *tasks,
        env=env,
    )


def lint(platform: str) -> None:
    env = environment(platform, build_native=False)
    tasks = ["ktlintCheck"]
    if platform == "android":
        tasks.append(":android:app:lintDebug")
    gradle(env, *tasks)
    if platform == "ios":
        native.run(
            "xcrun",
            "swift-format",
            "lint",
            "--strict",
            "--configuration",
            ".swift-format",
            "--recursive",
            "app/ios",
            env=env,
        )


def apple_environment(env: dict, configuration: str = "debug", sdk: str = "simulator") -> dict:
    app = contracts()["application"]
    architecture = "iosSimulatorArm64" if sdk == "simulator" else "iosArm64"
    flavor = "debug" if configuration == "debug" else "release"
    resources, bundle = compose_resource_paths(configuration, sdk, "Branch")
    env.update(
        BRANCH_IOS_MINIMUM_OS=contracts()["native-artifacts"]["ios"]["minimum_os"],
        BRANCH_BUNDLE_ID=app["bundle_id"],
        BRANCH_DISPLAY_NAME=app["display_name"],
        BRANCH_APP_VERSION=app["version"],
        BRANCH_BUILD_NUMBER=str(app["version_code"]),
        BRANCH_IOS_CONFIGURATION=configuration.capitalize(),
        BRANCH_COMPOSE_RESOURCES=str(resources),
        BRANCH_COMPOSE_BUNDLE=str(bundle),
        BRANCH_UI=str(
            output()
            / f"gradle/shared/xc-framework/bin/{architecture}/{flavor}Framework/BranchUI.framework"
        ),
    )
    return env


def xcode(
    env: dict, configuration: str, *args: str, project: Path | None = None, scheme: str = "Branch"
) -> None:
    native.run(
        "xcodebuild",
        "-project",
        str(project or (output() / "ios/project/Branch.xcodeproj")),
        "-scheme",
        scheme,
        "-configuration",
        configuration.capitalize(),
        "-derivedDataPath",
        str(output() / "ios/derived"),
        *args,
        env=env,
    )


SHARED_COMMON_TEST_MODULES = (
    (":shared:app", "shared/app"),
    (":catalog", "catalog"),
)
_SHARED_TEST_TARGETS = {
    "ios": "iosSimulatorArm64Test",
    "android": "testAndroidHostTest",
}


def compose_resource_paths(
    configuration: str,
    sdk: str,
    app_name: str,
) -> tuple[Path, Path]:
    architecture = "iosSimulatorArm64" if sdk == "simulator" else "iosArm64"
    source = (
        output()
        / f"gradle/shared/xc-framework/kotlin-multiplatform-resources/aggregated-resources/{architecture}/composeResources"
    )
    destination = (
        output()
        / "ios/derived/Build/Products"
        / f"{configuration.capitalize()}-{'iphonesimulator' if sdk == 'simulator' else 'iphoneos'}"
        / f"{app_name}.app/compose-resources/composeResources"
    )
    return source, destination


def verify_compose_resources(source: Path, destination: Path) -> None:
    if destination.parts[-2:] != ("compose-resources", "composeResources"):
        raise ValueError(f"Unbounded Compose resource destination: {destination}")
    if not source.is_dir():
        raise ValueError(f"Missing shared Compose resource bundle: {source}")


def common_test_directories() -> set[str]:
    return {
        str(path.parents[1].relative_to(ROOT / "app"))
        for path in (ROOT / "app").rglob("src/commonTest")
    }


def verify_shared_runners() -> None:
    declared = {directory for _, directory in SHARED_COMMON_TEST_MODULES}
    undeclared = common_test_directories() - declared
    if undeclared:
        raise ValueError(f"Modules declare commonTest without a runner: {sorted(undeclared)}")
    for _, directory in SHARED_COMMON_TEST_MODULES:
        if not (ROOT / "app" / directory / "src/commonTest").is_dir():
            raise ValueError(f"Declared shared test module has no commonTest: {directory}")


def executed_test_counts() -> dict[tuple[str, str], int]:
    base = output() / "gradle"
    counts: dict[tuple[str, str], int] = {}
    for path in sorted(base.rglob("TEST-*.xml")):
        parts = path.relative_to(base).parts
        if "test-results" not in parts:
            continue
        index = parts.index("test-results")
        key = ("/".join(parts[:index]), parts[index + 1])
        counts[key] = counts.get(key, 0) + int(ET.parse(path).getroot().get("tests", "0"))
    return counts


def build(platform: str, configuration: str = "debug", sdk: str = "simulator") -> dict:
    env = environment(platform)
    if platform == "android":
        tasks = [f":android:app:assemble{configuration.capitalize()}"]
        if configuration == "debug":
            tasks.append(":android:app:assembleDebugAndroidTest")
        gradle(env, *tasks)
    else:
        apple_environment(env, configuration, sdk)
        architecture = "iosSimulatorArm64" if sdk == "simulator" else "iosArm64"
        gradle(
            env,
            f":shared:xc-framework:link{configuration.capitalize()}Framework{architecture}",
            f":shared:xc-framework:assemble{architecture[0].upper()}{architecture[1:]}MainResources",
        )
        project = output() / "ios/project"
        project.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "app/ios/project.yml", project / "project.yml")
        native.run(
            "xcodegen",
            "generate",
            "--spec",
            str(project / "project.yml"),
            "--project",
            str(project),
            env=env,
        )
        destination = (
            "generic/platform=iOS Simulator" if sdk == "simulator" else "generic/platform=iOS"
        )
        verify_compose_resources(
            Path(env["BRANCH_COMPOSE_RESOURCES"]), Path(env["BRANCH_COMPOSE_BUNDLE"])
        )
        xcode(
            env,
            configuration,
            "-sdk",
            "iphonesimulator" if sdk == "simulator" else "iphoneos",
            "-destination",
            destination,
            "build",
        )
    return env


@contextlib.contextmanager
def ios_device():
    configured = os.environ.get("IOS_SIMULATOR_ID")
    spec = contracts()["development"]
    devices = json.loads(
        native.capture("xcrun", "simctl", "list", "devices", "available", "--json")
    )["devices"]
    if configured:
        matches = [d for group in devices.values() for d in group if d["udid"] == configured]
    else:
        matches = [
            d
            for d in devices.get(spec["ios_runtime"], [])
            if d["name"] == spec["ios_simulator_name"]
        ]
    if len(matches) > 1 or (configured and not matches):
        raise ValueError("Simulator selection is missing or ambiguous")
    udid = (
        matches[0]["udid"]
        if matches
        else native.capture(
            "xcrun",
            "simctl",
            "create",
            spec["ios_simulator_name"],
            spec["ios_device_type"],
            spec["ios_runtime"],
        )
    )
    owned = not matches or matches[0]["state"] != "Booted"
    try:
        if owned:
            native.run("xcrun", "simctl", "boot", udid)
        native.run("xcrun", "simctl", "bootstatus", udid, "-b")
        yield udid
    finally:
        if owned:
            subprocess.run(
                ["xcrun", "simctl", "shutdown", udid], check=False, stdout=subprocess.DEVNULL
            )


def adb(*args: str, serial: str | None = None) -> str:
    command = [str(native.sdk() / "platform-tools/adb")]
    if serial:
        command += ["-s", serial]
    return subprocess.check_output([*command, *args], text=True).strip()


@contextlib.contextmanager
def android_device():
    for key in ("ANDROID_USER_HOME", "ANDROID_AVD_HOME"):
        if os.environ.get(key):
            Path(os.environ[key]).mkdir(parents=True, exist_ok=True)
    selected = os.environ.get("ANDROID_SERIAL")
    process = None
    if not selected:
        spec = contracts()["development"]
        emulator = native.sdk() / "emulator/emulator"
        avds = subprocess.check_output([str(emulator), "-list-avds"], text=True).splitlines()
        if spec["android_avd"] not in avds:
            manager = cmdline_tool("avdmanager")
            subprocess.run(
                [
                    str(manager),
                    "create",
                    "avd",
                    "--name",
                    spec["android_avd"],
                    "--package",
                    spec["android_image"],
                    "--device",
                    "pixel_7",
                ],
                input="no\n",
                text=True,
                check=True,
            )
        existing = adb("devices")
        port = next((p for p in range(5580, 5680, 2) if f"emulator-{p}" not in existing), None)
        if port is None:
            raise ValueError("No available emulator slot")
        selected = f"emulator-{port}"
        log = output() / "android-emulator.log"
        with log.open("w") as stream:
            process = subprocess.Popen(
                [
                    str(emulator),
                    "-avd",
                    spec["android_avd"],
                    "-port",
                    str(port),
                    "-no-snapshot",
                    "-no-boot-anim",
                    "-gpu",
                    "swiftshader",
                    "-no-audio",
                ],
                stdout=stream,
                stderr=subprocess.STDOUT,
            )
    try:
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            if process and process.poll() is not None:
                raise ValueError("Emulator exited; inspect android-emulator.log")
            result = subprocess.run(
                [
                    str(native.sdk() / "platform-tools/adb"),
                    "-s",
                    selected,
                    "shell",
                    "getprop",
                    "sys.boot_completed",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip() == "1":
                break
            time.sleep(1)
        else:
            raise TimeoutError("Android device did not become ready")
        yield selected
    finally:
        if process:
            subprocess.run(
                [str(native.sdk() / "platform-tools/adb"), "-s", selected, "emu", "kill"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            try:
                process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=10)


def test(platform: str, configuration: str = "debug") -> None:
    if platform == "android" and configuration != "debug":
        raise ValueError("Android instrumentation tests support only the debug configuration")
    env = build(platform, configuration)
    if platform == "ios":
        with ios_device() as udid:
            xcode(env, configuration, "-destination", f"platform=iOS Simulator,id={udid}", "test")
    else:
        with android_device() as serial:
            env["ANDROID_SERIAL"] = serial
            gradle(env, ":android:app:connectedDebugAndroidTest")


def verify_shared_test_execution(
    platform: str,
    counts: dict[tuple[str, str], int],
) -> None:
    target = _SHARED_TEST_TARGETS[platform]
    for _, directory in SHARED_COMMON_TEST_MODULES:
        if counts.get((directory, target), 0) < 1:
            raise ValueError(f"No executed tests recorded for {directory}:{target}")


def test_shared(platform: str) -> None:
    verify_shared_runners()
    env = toolchain_environment()
    env["ANDROID_HOME"] = str(native.sdk())
    target = _SHARED_TEST_TARGETS[platform]
    tasks: list[str] = []
    for module, directory in SHARED_COMMON_TEST_MODULES:
        shutil.rmtree(output() / "gradle" / directory / "test-results", ignore_errors=True)
        tasks.append(f"{module}:{target}")
    if platform == "ios":
        with ios_device():
            gradle(env, *tasks)
    else:
        gradle(env, *tasks)
    verify_shared_test_execution(platform, executed_test_counts())


def test_shared_all() -> None:
    test_shared("android")
    test_shared("ios")


def dev(platform: str) -> None:
    env = build(platform)
    bundle = contracts()["application"]["bundle_id"]
    if platform == "ios":
        with ios_device() as udid:
            native.run("open", "-a", "Simulator", "--args", "-CurrentDeviceUDID", udid)
            native.run(
                "xcrun",
                "simctl",
                "install",
                udid,
                str(output() / "ios/derived/Build/Products/Debug-iphonesimulator/Branch.app"),
            )
            native.run("xcrun", "simctl", "launch", "--console-pty", udid, bundle, env=env)
    else:
        with android_device() as serial:
            adb(
                "install",
                "-r",
                str(output() / "gradle/android/app/outputs/apk/debug/app-debug.apk"),
                serial=serial,
            )
            adb("shell", "am", "start", "-n", f"{bundle}/.MainActivity", serial=serial)
            native.run(
                str(native.sdk() / "platform-tools/adb"),
                "-s",
                serial,
                "logcat",
                "--pid=" + adb("shell", "pidof", bundle, serial=serial),
            )


def catalog_apple_environment(
    env: dict, configuration: str = "debug", sdk: str = "simulator"
) -> dict:
    app = contracts()["application"]
    architecture = "iosSimulatorArm64" if sdk == "simulator" else "iosArm64"
    flavor = "debug" if configuration == "debug" else "release"
    resources, bundle = compose_resource_paths(configuration, sdk, "BranchCatalog")
    env.update(
        BRANCH_IOS_MINIMUM_OS=contracts()["native-artifacts"]["ios"]["minimum_os"],
        BRANCH_APP_VERSION=app["version"],
        BRANCH_BUILD_NUMBER=str(app["version_code"]),
        BRANCH_CATALOG_UI=str(
            output()
            / f"gradle/catalog/xc-framework/bin/{architecture}/{flavor}Framework/BranchCatalogUI.framework"
        ),
        BRANCH_COMPOSE_RESOURCES=str(resources),
        BRANCH_COMPOSE_BUNDLE=str(bundle),
    )
    return env


def catalog_project() -> Path:
    project = output() / "ios/catalog-project"
    project.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "app/catalog/ios/project.yml", project / "project.yml")
    return project


def build_catalog(platform: str, configuration: str = "debug", sdk: str = "simulator") -> dict:
    env = toolchain_environment()
    if platform == "android":
        env["ANDROID_HOME"] = str(native.sdk())
        gradle(env, f":catalog:android:assemble{configuration.capitalize()}")
    else:
        catalog_apple_environment(env, configuration, sdk)
        architecture = "iosSimulatorArm64" if sdk == "simulator" else "iosArm64"
        gradle(
            env,
            f":catalog:xc-framework:link{configuration.capitalize()}Framework{architecture}",
            f":shared:xc-framework:assemble{architecture[0].upper()}{architecture[1:]}MainResources",
        )
        project = catalog_project()
        native.run(
            "xcodegen",
            "generate",
            "--spec",
            str(project / "project.yml"),
            "--project",
            str(project),
            env=env,
        )
        destination = (
            "generic/platform=iOS Simulator" if sdk == "simulator" else "generic/platform=iOS"
        )
        verify_compose_resources(
            Path(env["BRANCH_COMPOSE_RESOURCES"]), Path(env["BRANCH_COMPOSE_BUNDLE"])
        )
        xcode(
            env,
            configuration,
            "-sdk",
            "iphonesimulator" if sdk == "simulator" else "iphoneos",
            "-destination",
            destination,
            "build",
            project=project / "BranchCatalog.xcodeproj",
            scheme="BranchCatalog",
        )
    return env


def test_catalog(platform: str, configuration: str = "debug") -> None:
    if platform == "android":
        if configuration != "debug":
            raise ValueError("Android instrumentation tests support only the debug configuration")
        env = build_catalog("android", configuration)
        with android_device() as serial:
            env["ANDROID_SERIAL"] = serial
            gradle(env, ":catalog:android:connectedDebugAndroidTest")
    else:
        env = build_catalog("ios", configuration)
        with ios_device() as udid:
            xcode(
                env,
                configuration,
                "-destination",
                f"platform=iOS Simulator,id={udid}",
                "test",
                project=catalog_project() / "BranchCatalog.xcodeproj",
                scheme="BranchCatalog",
            )


def dev_catalog(platform: str) -> None:
    env = build_catalog(platform)
    if platform == "ios":
        with ios_device() as udid:
            native.run("open", "-a", "Simulator", "--args", "-CurrentDeviceUDID", udid)
            native.run(
                "xcrun",
                "simctl",
                "install",
                udid,
                str(
                    output() / "ios/derived/Build/Products/Debug-iphonesimulator/BranchCatalog.app"
                ),
            )
            native.run(
                "xcrun",
                "simctl",
                "launch",
                "--console-pty",
                udid,
                "ai.arboresce.branch.catalog",
                env=env,
            )
    else:
        with android_device() as serial:
            apks = sorted((output() / "gradle/catalog/android/outputs/apk/debug").glob("*.apk"))
            if not apks:
                raise ValueError("Catalog Android APK is missing; run the catalog build")
            adb("install", "-r", str(apks[0]), serial=serial)
            adb(
                "shell",
                "am",
                "start",
                "-n",
                "ai.arboresce.branch.catalog/.host.CatalogActivity",
                serial=serial,
            )
            native.run(
                str(native.sdk() / "platform-tools/adb"),
                "-s",
                serial,
                "logcat",
                "--pid=" + adb("shell", "pidof", "ai.arboresce.branch.catalog", serial=serial),
            )


def setup(platform: str) -> None:
    configure(write=True)
    native.run("rustup", "target", "add", *contracts()["native-artifacts"][platform]["targets"])
    if platform == "android":
        spec = contracts()["native-artifacts"]["android"]
        manager = cmdline_tool("sdkmanager")
        native.run(
            manager,
            f"--sdk_root={native.sdk()}",
            "platform-tools",
            f"platforms;android-{spec['compile_sdk']}",
            "build-tools;36.0.0",
            f"ndk;{spec['ndk']}",
            "emulator",
            contracts()["development"]["android_image"],
        )
    build(platform, "debug")
