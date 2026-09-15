# Repository layout

The Branch project directory owns its Cargo workspace, contracts and Make command
routing. Documentation paths and commands are relative to that directory, even
when the project is hosted in a larger Git checkout.

core/domain owns domain state; core/runtime owns its lifecycle. app/rust/runtime-ffi owns the
foreign interface. These crates share one Cargo.lock and retain independent package
identities. tools/bindgen and tools/native-build own binding generation and verification.

app owns the Gradle build and wrapper. app/android/app and app/ios own native hosts.
app/ui/diagnostic/public owns the shared screen; app/shared/xc-framework owns the
Swift-facing Compose entry point. app/ios/Runtime retains the Swift runtime adapter.
Generated bindings never become handwritten UI APIs. Rust remains authoritative.

Gradle project identities are explicit in app/settings.gradle.kts. Output directories
use complete project paths so repeated leaf names cannot collide. docs owns existing
specifications and setup guidance. Generated products belong in ignored .build or an
explicitly selected external output directory. Root Make commands remain unchanged.
