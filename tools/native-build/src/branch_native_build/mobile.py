import contextlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from . import native
from .config import ROOT, configure, contracts, output


def environment(platform: str, build_native: bool = True) -> dict:
    path = native.build(platform) if build_native else native.check(platform)
    env = dict(
        os.environ, BRANCH_ROOT=str(ROOT), BRANCH_BUILD_DIR=str(output()), BRANCH_NATIVE=str(path)
    )
    if not env.get("JAVA_HOME"):
        env["JAVA_HOME"] = native.capture("/usr/libexec/java_home", "-v", "21")
    if platform == "android":
        env["ANDROID_HOME"] = str(native.sdk())
    return env


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
    env.update(
        BRANCH_IOS_MINIMUM_OS=contracts()["native-artifacts"]["ios"]["minimum_os"],
        BRANCH_BUNDLE_ID=app["bundle_id"],
        BRANCH_DISPLAY_NAME=app["display_name"],
        BRANCH_APP_VERSION=app["version"],
        BRANCH_BUILD_NUMBER=str(app["version_code"]),
        BRANCH_IOS_CONFIGURATION=configuration.capitalize(),
        BRANCH_UI=str(
            output()
            / f"gradle/shared/xc-framework/bin/{architecture}/{flavor}Framework/BranchUI.framework"
        ),
    )
    return env


def xcode(env: dict, configuration: str, *args: str) -> None:
    native.run(
        "xcodebuild",
        "-project",
        str(output() / "ios/project/Branch.xcodeproj"),
        "-scheme",
        "Branch",
        "-configuration",
        configuration.capitalize(),
        "-derivedDataPath",
        str(output() / "ios/derived"),
        *args,
        env=env,
    )


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
            manager = native.sdk() / "cmdline-tools/19.0/bin/avdmanager"
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
    env = build(platform, configuration)
    if platform == "ios":
        with ios_device() as udid:
            xcode(env, configuration, "-destination", f"platform=iOS Simulator,id={udid}", "test")
    else:
        with android_device() as serial:
            env["ANDROID_SERIAL"] = serial
            gradle(env, ":android:app:connectedDebugAndroidTest")


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


def setup(platform: str) -> None:
    configure(write=True)
    native.run("rustup", "target", "add", *contracts()["native-artifacts"][platform]["targets"])
    if platform == "android":
        spec = contracts()["native-artifacts"]["android"]
        manager = native.sdk() / "cmdline-tools/19.0/bin/sdkmanager"
        native.run(
            str(manager),
            f"--sdk_root={native.sdk()}",
            "platform-tools",
            f"platforms;android-{spec['compile_sdk']}",
            "build-tools;36.0.0",
            f"ndk;{spec['ndk']}",
            "emulator",
            contracts()["development"]["android_image"],
        )
    build(platform, "debug")
