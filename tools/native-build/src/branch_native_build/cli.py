import argparse

from . import config, native


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=[
            "config-write",
            "config-check",
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
    args = parser.parse_args()
    config.local_environment()
    if args.action.startswith("config-"):
        config.configure(args.action == "config-write")
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

            getattr(mobile, args.action)(args.platform)


if __name__ == "__main__":
    main()
