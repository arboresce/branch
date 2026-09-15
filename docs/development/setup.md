# Setup

The initial native build lane runs on macOS. Install Xcode 26.6 (including command-line
tools, swift-format and the iOS 26.5 simulator runtime), XcodeGen, JDK 21, uv with Python 3.14,
and rustup. The committed toolchain selects Rust 1.98.0. Rust-only checks do not
require a mobile SDK. Run `make doctor` to inspect the host tools.

For Android, install Android SDK command-line tools 19.0 and set ANDROID_HOME.
The setup command installs the contract-selected SDK, build tools, NDK and emulator
image. External tool installation and SDK license acceptance belong to the developer.

Create an optional ignored `.env.local` containing plain KEY=value lines:

```dotenv
ANDROID_HOME=/absolute/path/to/android-sdk
JAVA_HOME=/absolute/path/to/jdk-21/Contents/Home
BRANCH_BUILD_DIR=/absolute/path/to/branch-build
```

Omit BRANCH_BUILD_DIR to use ignored `.build`. Existing environment variables take
precedence. Do not quote or source the file as shell. Only ANDROID_HOME, JAVA_HOME,
BRANCH_BUILD_DIR, IOS_SIMULATOR_ID and ANDROID_SERIAL are accepted. No local file
or credential is packaged in either app. To reuse a particular running device,
set its exact simulator UDID or adb serial in this file. Otherwise the runner uses
its named Branch development simulator/AVD and shuts it down after the command.

```sh
make setup-rust
make verify-rust
make setup-android
make dev-android
make setup-ios
make dev-ios
```

Setup is required before check on a fresh checkout: check rejects missing artifacts
and does not repair them. Gradle downloads its checksum-pinned distribution and
verified dependencies. Native outputs stay outside source under the selected build
directory; never copy arbitrary generated bindings or libraries into app source.

The default iOS app build targets the Apple Silicon simulator. Rust and shared UI
also compile device slices. Installing on physical iOS hardware requires a separate
signing configuration; no signing team or production keys are supplied. Android
builds include arm64-v8a and x86_64; the default emulator uses arm64-v8a.
