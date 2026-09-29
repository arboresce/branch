import argparse
import json
import sys

from . import config, native

_PLATFORM_ACTIONS = {
    "build-native",
    "check-native",
    "lint",
    "build",
    "setup",
    "test",
    "dev",
    "build-catalog",
    "test-catalog",
    "dev-catalog",
}
_NO_PLATFORM_ACTIONS = {
    "config-write",
    "config-check",
    "contract-check",
    "env-check",
    "test-shared",
    "test-shared-android",
    "test-shared-ios",
}
_CONFIGURATION_ACTIONS = {"build", "test", "build-catalog", "test-catalog"}
_SDK_ACTIONS = {"build", "test", "build-catalog", "test-catalog"}
_TEST_ACTIONS = {"test", "test-catalog"}
_BUILD_ACTIONS = {"build", "build-catalog"}


def resolve(
    action: str,
    platform: str | None,
    configuration: str | None,
    sdk: str | None,
) -> tuple[str | None, str, str]:
    if action in _NO_PLATFORM_ACTIONS:
        if platform is not None or configuration is not None or sdk is not None:
            raise ValueError(f"{action} does not accept a platform or build options")
        return None, "debug", "simulator"
    if platform is None:
        raise ValueError(f"{action} requires an explicit platform")
    if action not in _CONFIGURATION_ACTIONS and configuration is not None:
        raise ValueError(f"{action} does not accept a configuration option")
    if action not in _SDK_ACTIONS and sdk is not None:
        raise ValueError(f"{action} does not accept an sdk option")
    resolved_configuration = configuration or "debug"
    resolved_sdk = sdk or "simulator"
    if action in _TEST_ACTIONS:
        if platform == "android" and resolved_configuration != "debug":
            raise ValueError("Android instrumentation tests support only the debug configuration")
        if resolved_sdk != "simulator":
            raise ValueError("Device test execution is not supported; use a simulator or emulator")
    if action in _BUILD_ACTIONS and platform == "android" and resolved_sdk != "simulator":
        raise ValueError("Android application builds do not support the device sdk")
    return platform, resolved_configuration, resolved_sdk


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=[
            "config-write",
            "config-check",
            "contract-check",
            "env-check",
            "test-shared",
            "test-shared-android",
            "test-shared-ios",
            "build-native",
            "check-native",
            "lint",
            "build",
            "setup",
            "test",
            "dev",
            "build-catalog",
            "test-catalog",
            "dev-catalog",
        ],
    )
    parser.add_argument("platform", choices=["ios", "android"], nargs="?")
    parser.add_argument("--configuration", choices=["debug", "release"], default=None)
    parser.add_argument("--sdk", choices=["simulator", "device"], default=None)
    args = parser.parse_args()
    config.local_environment()
    try:
        platform, configuration, sdk = resolve(
            args.action, args.platform, args.configuration, args.sdk
        )
    except ValueError as error:
        parser.error(str(error))
    if args.action.startswith("config-"):
        config.configure(args.action == "config-write")
    elif args.action.startswith("test-shared"):
        from . import mobile

        if args.action == "test-shared":
            mobile.test_shared_all()
        else:
            mobile.test_shared(args.action.removeprefix("test-shared-"))
    elif args.action == "contract-check":
        from . import inventory

        print(json.dumps(inventory.validate(), sort_keys=True))
    elif args.action == "env-check":
        from . import environment

        problems = environment.environment_problems(
            config.ROOT / "tools/native-build/uv.lock", environment.installed_versions()
        )
        for problem in problems:
            print(problem, file=sys.stderr)
        if problems:
            raise SystemExit(1)
        print("Python tool environment is synchronized with the lockfile")
    elif args.action in {"build-native", "check-native"}:
        print(native.build(platform) if args.action == "build-native" else native.check(platform))
    else:
        from . import mobile

        if args.action == "build":
            mobile.build(platform, configuration, sdk)
        elif args.action == "test":
            mobile.test(platform, configuration)
        elif args.action == "build-catalog":
            mobile.build_catalog(platform, configuration, sdk)
        elif args.action == "test-catalog":
            mobile.test_catalog(platform, configuration)
        elif args.action == "dev-catalog":
            mobile.dev_catalog(platform)
        else:
            getattr(mobile, args.action)(platform)


if __name__ == "__main__":
    main()
