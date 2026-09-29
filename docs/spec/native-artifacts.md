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
the one supported release-profile override; unset normalizes to `3`, the supported
values are `0`, `1`, `2`, `3`, `s` and `z`, and other values are rejected.
Any other `CARGO_PROFILE_*` override, including the development profile used by
host bindgen, is rejected before cache lookup rather than leaking into the producer.
The supported producer uses the pinned default Rust toolchain and platform-selected
linkers. Explicit `RUSTC`, `RUSTC_WRAPPER`, `RUSTC_WORKSPACE_WRAPPER`, their Cargo
aliases and caller/configuration-selected target linkers are unsupported and must
be rejected before cache lookup. This bounded policy supersedes the earlier
proposal to support arbitrary compiler/wrapper selectors by recording their paths.
Recorded semantic inputs include the actual default compiler identity and supported
flag variables (`RUSTFLAGS`, `CARGO_ENCODED_RUSTFLAGS`, `CARGO_BUILD_RUSTFLAGS`).
Any retained per-target rustflags include the native host as well as all produced
targets; unsupported target settings fail explicitly. Output and cache locations such as
`CARGO_TARGET_DIR`, `BRANCH_BUILD_DIR` and `BRANCH_NATIVE` are explicitly not
semantic inputs. Identity and subprocess execution share the same validated policy;
the whole host environment is never hashed and credentials are never printed.

The supported-input list is closed for code-generation semantics, not merely a
list of values to hash while inheriting all others. Compiler/default-target aliases
including `CARGO_BUILD_RUSTC` and `CARGO_BUILD_TARGET`, and unmodeled incremental,
profile or host-target overrides must fail before cache lookup. Compiler identity
must describe the executable/toolchain actually invoked. Applicable repository,
ancestor and selected Cargo-home configuration
must be evaluated for build-affecting settings and normalized or rejected by the
same resolver. Do not copy those files or hash credential/registry configuration.
Output/cache routing remains nonsemantic. Producer-selected linker settings must
be the settings represented by identity. The host bindgen build follows this same
policy, and unsupported NDK host architectures/prebuilt directories fail explicitly.
Nonempty Cargo `[env]` tables and configuration profile overrides are unsupported:
reject them before identity serialization or execution. Diagnostics name the key
or category without echoing values. Never persist Cargo `[env]` values or credentials
in cohort manifests. Normalize output/cache-only Cargo settings out of semantic
identity. Regression tests must observe both identity decisions and the actual
environment/arguments passed to host and target build/bindgen subprocesses.

Gradle versions live in app/gradle/libs.versions.toml and the wrapper properties. Resolution
locks and verification-metadata.xml are committed. contracts/native-settings.properties
is a deterministic projection; Python checks compare its exact bytes. Android's
preBuild checks the selected native cohort. iOS orchestration checks it before Xcode.

The Python producer uses only the Python standard library plus pinned jsonschema;
its tests exercise contract rejection, deterministic settings and tampered artifacts.
A Python environment may be selected with UV_PROJECT_ENVIRONMENT. This is a tooling
location, not a runtime value or bundled application configuration.
