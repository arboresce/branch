# Mobile bootstrap checkpoints

## Accepted scope

Independent Rust core/runtime/FFI, a shared Compose diagnostic screen and Android/iOS
hosts. Only preview JSON is displayed. Native targets and metadata are contract-owned.

## Checkpoint 1 — Rust foundation

Implemented state, snapshot lifecycle, compiler metadata, UniFFI facade and repository
documentation. Verification: make verify-rust passed (format, locked workspace check, Clippy
with warnings denied, five unit tests and documentation tests).

## Checkpoint 2 — Native artifact production

Implemented closed TOML schemas, deterministic settings, source-addressed native
cohorts and integrity validation. Five Python tests passed. Rust libraries and
bindings were generated for both Android ABIs and the iOS device/simulator targets.

## Checkpoint 3 — Mobile hosts

Gradle uses committed wrapper checksums, resolution locks and dependency verification.
Android consumes generated Kotlin bindings and both native ABIs. The iOS Swift host
consumes its Rust XCFramework and the shared Compose framework. Both hosts display
one selectable, scrollable JSON screen without navigation.

Verification on 2026-09-15: Android debug and instrumentation builds passed; one
instrumented test passed on Android 16/arm64. Visual inspection confirmed actual
Rust metadata. The iOS simulator app built and both XCTest tests passed: the native
snapshot/shutdown test and the UI launch/visible-snapshot test. iOS simulator 26.5
ran on Apple Silicon with Xcode 26.6. Both platform check commands passed, including
Rust formatting/check/Clippy, five Python tests, settings and artifact integrity.
Runners shut down their owned devices after tests.

The iOS launch test caught a missing Compose frame-duration plist property; the
project now explicitly generates that boolean property. Physical Android/iOS
installation, iOS signing, release distribution and remote consumer availability
are not qualified.

## Checkpoint 4 — Independent local checkout

A fresh local Git clone of 0da95a6 built Android and iOS from its committed sources,
using a separate Python environment and output directory. make verify-rust, both
platform builds and both platform checks passed. Dependency download/compiler
caches were reused; generated native cohorts and host products were rebuilt in
the new output directory. The clone remained clean after verification. This proves
the exercised local standalone build paths; it is not a remote-origin availability
receipt or a cold-cache/network qualification.
