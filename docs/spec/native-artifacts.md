# Native artifact contract

contracts/native-artifacts.toml owns platform targets, OS floors, NDK and UniFFI pins.
Application identity comes from contracts/application.toml. Producers must validate
contracts before building and reject stale settings without automatic repair in check.

Native builds produce source-addressed cohorts containing bindings, platform libraries
and an integrity manifest. Apple uses device/simulator slices; Android uses ABI-specific
JNI libraries. Source, toolchain, target and configuration identities must participate
in the cohort identity. Consumers verify the manifest before compilation.

Generated bindings and libraries are build outputs, never handwritten source. Public
source must not contain developer paths, runtime credentials or opaque local state.

The current producer hashes Cargo inputs, Rust sources, concrete contracts, schemas,
bindgen and producer sources, the Python lockfile, compiler identity and platform
SDK identity. A manifest verifies every output byte; a source change during generation
aborts installation. Writes stage beside the final cohort and rename only after
verification. Existing mismatched cohorts are never silently repaired.

Cohort identity describes the effective build. `CARGO_PROFILE_RELEASE_OPT_LEVEL` is
the one supported release-profile override; unset normalizes to `3` and other values
are rejected. Any other `CARGO_PROFILE_RELEASE_*` override (`LTO`, `DEBUG`, `PANIC`
and similar) is rejected before cache lookup rather than leaking into the producer.
Recorded semantic inputs include compiler and wrapper selection (`RUSTC`,
`RUSTC_WRAPPER`, `RUSTC_WORKSPACE_WRAPPER`), flag variables (`RUSTFLAGS`,
`CARGO_ENCODED_RUSTFLAGS`, `CARGO_BUILD_RUSTFLAGS`), per-target linker and rustflag
overrides and an existing `.cargo/config.toml`. Output and cache locations such as
`CARGO_TARGET_DIR`, `BRANCH_BUILD_DIR` and `BRANCH_NATIVE` are explicitly not
semantic inputs. Identity and subprocess execution share the same validated policy;
the whole host environment is never hashed and credentials are never printed.

Gradle versions live in app/gradle/libs.versions.toml and the wrapper properties. Resolution
locks and verification-metadata.xml are committed. contracts/native-settings.properties
is a deterministic projection; Python checks compare its exact bytes. Android's
preBuild checks the selected native cohort. iOS orchestration checks it before Xcode.

The Python producer uses only the Python standard library plus pinned jsonschema;
its tests exercise contract rejection, deterministic settings and tampered artifacts.
A Python environment may be selected with UV_PROJECT_ENVIRONMENT. This is a tooling
location, not a runtime value or bundled application configuration.
