# Mobile bootstrap checkpoints

## Accepted scope

Independent Rust core/runtime/FFI, a shared Compose diagnostic screen and Android/iOS
hosts. Only preview JSON is displayed. Native targets and metadata are contract-owned.

Checkpoints 1-4 below are historical bootstrap receipts from the pre-adoption
history. Their dates, environment details and revision identifiers (including the
checkpoint 4 clone of `0da95a6`) describe the bootstrap repository, not the current
adopted checkout; `0da95a6` is not present in this repository's history. They are
retained as evidence and are not re-presented as fresh. The current baseline is
recorded at the end of this document.

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

## Baseline record — 2026-09-28

The adopted checkout was inspected at initial commit `68338c0` before UI Foundation
execution. Recorded environment: rustc/cargo 1.98.0, uv 0.12.19, Python 3.14.7,
Xcode 26.6 (17F113), iOS simulator SDK 26.5, JDK 21 (Temurin), Android SDK
platform android-36, build-tools 36.0.0 and NDK 29.0.14206865 under the selected
external build root.

Baseline commands (all exit zero):

- `make verify-rust` — cargo fmt/clippy/check plus `cargo test --workspace --locked`:
  five unit tests passed (branch-domain 1, branch-runtime 3, branch-runtime-ffi 1),
  zero failures.
- `branch-native config-check` — deterministic settings projection matched.
- Python package tests — five tests passed at baseline; the UI Foundation inventory
  work adds contract validation cases recorded in the BDS-00 execution ledger.

Generated native cohorts for both platforms were already present under the selected
build root from the earlier bootstrap; they are local build outputs, not committed
source. No whole-checkout qualification is claimed here, and no historical receipt
is relabelled as fresh.

## Checkpoint 4 — Independent local checkout

A fresh local Git clone of 0da95a6 built Android and iOS from its committed sources,
using a separate Python environment and output directory. make verify-rust, both
platform builds and both platform checks passed. Dependency download/compiler
caches were reused; generated native cohorts and host products were rebuilt in
the new output directory. The clone remained clean after verification. This proves
the exercised local standalone build paths; it is not a remote-origin availability
receipt or a cold-cache/network qualification.
