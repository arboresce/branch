import argparse
import json

from . import config, native


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=[
            "config-write",
            "config-check",
            "contract-check",
            "build-native",
            "check-native",
            "lint",
            "build",
            "setup",
            "test",
            "dev",
        ],
    )
    parser.add_argument("platform", choices=["ios", "android"], nargs="?")
    parser.add_argument("--configuration", choices=["debug", "release"], default="debug")
    parser.add_argument("--sdk", choices=["simulator", "device"], default="simulator")
    args = parser.parse_args()
    config.local_environment()
    if args.action.startswith("config-"):
        config.configure(args.action == "config-write")
    elif args.action == "contract-check":
        from . import inventory

        print(json.dumps(inventory.validate(), sort_keys=True))
    else:
        if not args.platform:
            parser.error("platform is required")
        if args.action in {"build-native", "check-native"}:
            print(
                native.build(args.platform)
                if args.action == "build-native"
                else native.check(args.platform)
            )
        else:
            from . import mobile

            if args.action == "build":
                mobile.build(args.platform, args.configuration, args.sdk)
            elif args.action == "test":
                mobile.test(args.platform, args.configuration)
            else:
                getattr(mobile, args.action)(args.platform)


if __name__ == "__main__":
    main()
