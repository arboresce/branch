# Commands

All commands are explicit Make targets routed through scripts/commands.sh. No
caller TARGET selector is supported. Commands run from the Branch project directory
containing this Makefile.

| Command | Behavior |
| --- | --- |
| make help | List supported developer commands |
| make doctor | Inspect Rust, uv, Xcode, swift-format, XcodeGen and JDK availability |
| make setup-rust | Fetch locked Rust dependencies |
| make check-rust | Check formatting, compilation and Clippy |
| make test-rust | Run Rust unit and documentation tests |
| make test-shared | Run the Kotlin shared-module tests on the iOS simulator and the Android host runner |
| make test-shared-android / test-shared-ios | Run the shared-module common tests on the Android host JVM or the iOS simulator |
| make check-tools | Check the locked Python environment, contracts, native settings, Python tests and style without a platform SDK |
| make verify-rust | Run Rust checks, then tests |
| make setup-android / setup-ios | Prepare locked Python tools, platform Rust targets, settings, bindings and debug app |
| make build-android / build-ios | Verify settings, build/reuse verified native artifacts and build the debug app |
| make build-release-android | Build the release Android app variant; no signing identity is invented |
| make build-catalog-android / build-catalog-ios | Build the separate development catalog application (`ai.arboresce.branch.catalog`) for Android or the iOS simulator |
| make build-release-catalog-ios | Build the catalog Release simulator framework and app with its own aggregated resources |
| make build-catalog-ios-device | Build the catalog Release device framework and app unsigned where local tooling permits |
| make dev-catalog-android / dev-catalog-ios | Build, install and launch the catalog app; not a production build |
| make test-catalog-android / test-catalog-ios | Run the catalog host rendering tests on an emulator or simulator |
| make build-release-ios | Build and link the Release simulator framework and app |
| make build-ios-device | Build the Release device framework and app where local signing/tooling permits |
| make dev-android / dev-ios | Build, install and launch, retaining foreground console attachment |
| make check-android / check-ios | Check Rust, Python tests/style, Kotlin style, settings and native artifact integrity; Android also runs Android Lint for the production and catalog hosts; iOS runs Swift style over both host trees. No repairs |
| make test-android / test-ios | Build, boot/select a device and execute native platform tests |
| make verify-android / verify-ios | Check first, then run platform tests |
| make setup / check / test / verify | Apply the corresponding action to Android, then iOS |

Setup may install missing Android packages through sdkmanager; accept its license
prompts as the developer. Build/check never rewrite contracts or dependency locks.
Checks first verify the Python tool lockfile and selected environment
(`uv lock --check`, `uv sync --check`) plus exact direct-dependency versions and
Ruff availability; they report the setup command instead of repairing.
`check-native-android` and `check-native-ios` are internal Bash dispatcher entries
used by build integration, not extra Make targets. The internal `branch-native lint`
action runs pinned Gradle ktlint checks for handwritten Kotlin and build scripts;
on iOS it also runs Xcode swift-format over `app/ios` and `app/catalog/ios` with the
committed `.swift-format` settings, and on Android it runs Android Lint for both the
production and catalog application hosts. Generated bindings are excluded from style
checks.

Dev is an interactive foreground command, not a background service. Ctrl-C closes
its console and shuts down only a simulator/emulator booted by that invocation.
An explicitly selected, already-running device remains running. There is no hot
reload: rebuild/restart for source changes. No network services are started.
