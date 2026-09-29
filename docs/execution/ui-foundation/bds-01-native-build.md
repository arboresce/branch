# BDS-01: Native integrity and build profiles

Status: second-review correction complete, independent acceptance pending, 2026-09-29.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-01, BUI-02.
Prerequisites: [BDS-00](bds-00-contracts.md).
Next action: await independent acceptance; retain the accepted routing and environment checks.

## Scope

- `tools/native-build/src/branch_native_build/native.py`
- `tools/native-build/src/branch_native_build/config.py`
- `tools/native-build/src/branch_native_build/mobile.py`
- `tools/native-build/src/branch_native_build/cli.py`
- `tools/native-build/tests/`
- `contracts/native-artifacts.toml and its schema/settings projection`
- `app/ios/project.yml`
- `scripts/commands.sh`
- `Makefile`
- `docs/spec/native-artifacts.md`
- `docs/development/`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

No new component export is owned by this unit.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-01.01 | complete | Close remaining effective native-input gaps | V1 |
| BDS-01.02 | complete | Close manifest integrity gap | V1 |
| BDS-01.03 | complete | Correct explicit build/test profile routing | V1, V2 |
| BDS-01.04 | complete | Verify locked environment freshness | V1, V6 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-01.01: Control effective native configuration

Scope: Specify normalized/rejected build environment inputs and version identity; include supported overrides, targets, SDK/configuration and producer inputs without host secrets.

Definition of green: Profile override changes identity or fails; deployment-target mismatch cannot silently reuse a cohort; controlled equivalent inputs remain stable.

Verify lane: V1. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-01.02: Close manifest integrity gap

Scope: Exclude only the cohort-root metadata file; verify nested manifests and all declared outputs; retain symlink and stale-selection checks.

Definition of green: Nested-manifest tampering and unexpected nested files fail; normal manifest verification, missing-file and byte-change tests pass.

Verify lane: V1. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-01.03: Separate native UI build profiles

Scope: Select framework paths by SDK, target and configuration; add explicit simulator Release and future device build routing without store/signing assumptions.

Definition of green: Both simulator configurations consume correct frameworks/resources; device framework compiles where tooling permits; no false device-run claim.

Verify lane: V1, V2. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-01.04: Make environment setup reproducible

Scope: Prepare the selected locked Python environment; diagnose absent dependencies in checks; preserve existing Make behavior and documented external-output routing.

Definition of green: An independently prepared environment runs the documented check path; checks do not repair dependencies/contracts/locks.

Verify lane: V1, V6. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

## Verification and checkpoint record

[Lane definitions and completion policy](../../spec/ui-foundation.md#bui-11-verification-and-completion)
are normative. Run narrow changed-module checks per slice and declared integrated
checks at the unit boundary. Existing applicable commands include `make verify-rust`,
`make check-android`, `make check-ios`, `make test-android` and `make test-ios`;
none substitutes for an uncovered new shared-UI or physical-device lane.

Record actual commands/exit codes, test names/counts, target/tool versions,
configuration, relevant resources and portable evidence paths. Use planned,
active, verified-uncommitted, complete or blocked per slice. Mark complete only
after its required checks and authorized checkpoint exist; record actual revision
in the next ledger update. No commit/push/publication is authorized by a status.
Never mark a device-only result passed from a simulator run.

Checkpoint evidence: submitted commits `2030bcb`, `127bc05`, `6080be2`, `7bf20fc`; BDS-01.02 retained complete; BDS-01.01 corrected at `beefd3d`, BDS-01.03 at `eaf92a5`, BDS-01.04 at `7d3ca29` on 2026-09-29.
Current implementation slice: none.
Open failures/limits: F08/F09 accepted; R2-01 corrected in the second-review batch. Linux producer execution and hosted CI remain NOT_RUN; host-tag tests are not Linux execution evidence.

## Second-review amendment (2026-09-29)

R2-01 / BDS-01.01: `CARGO_BUILD_RUSTC`, `CARGO_BUILD_TARGET` and
`CARGO_INCREMENTAL` still reach producer subprocesses without affecting identity
or being rejected. Only the repository-local Cargo configuration is inspected;
Cargo also reads ancestor and selected Cargo-home configuration. Compiler/wrapper
path strings alone do not identify the executable actually used.

Apply the clarified policy in [native artifacts](../../spec/native-artifacts.md).
Use one effective-input resolver before cache lookup and subprocess construction,
including host bindgen compilation. Reject unsupported compiler/default-target and
profile aliases, model any retained flags and wrappers by their effective meaning,
and account for applicable configuration without copying credentials or host
configuration into the repository. Keep build-output routing operational. Reject
unsupported NDK host architectures and mismatched prebuilt directories; do not
fall back to the only directory when it belongs to another host.

Acceptance requires negative tests for the three demonstrated aliases, ancestor
and Cargo-home semantic config, actual compiler/wrapper identity or rejection,
host-target overrides and mismatched NDK hosts. Check actual subprocess arguments
and environment as well as hash changes. Preserve all previously passing integrity,
deployment-target, routing and exact Python readiness checks. Linux execution
remains separately reported if no Linux environment is available.

## Review amendment (2026-09-29)

- F01 / BDS-01.01: changing `CARGO_PROFILE_RELEASE_LTO`,
  `CARGO_PROFILE_RELEASE_DEBUG` or `CARGO_PROFILE_RELEASE_PANIC` leaves the cohort
  identity unchanged while the producer inherits those variables. Adopt a bounded
  effective-input policy: retain the approved optimization override, reject other
  unsupported profile overrides, and normalize or reject compiler, wrapper,
  target/linker/flags, SDK and applicable Cargo-config inputs before cache lookup.
  Explicitly distinguish output/cache paths from semantic inputs. Use the same
  policy for identity and subprocess execution; never hash the whole environment
  or print credentials. Add meaningful regressions beyond the original two cases,
  including stale cohort reuse and equivalent supported settings. Preserve the
  deployment-target and nested-manifest fixes.
- F09 / BDS-01.03: requesting Android Release tests currently builds Release but
  executes `connectedDebugAndroidTest`. Until a separate Release instrumentation
  lane is specified, reject non-Debug Android test requests before building.
  Reject SDK/configuration arguments unsupported by an action instead of silently
  ignoring them. Preserve all three new Release/device build commands and prove
  their framework/resource routing with invocation tests and host builds.
- F08 / BDS-01.04: importing `jsonschema` and `pytest` does not establish a locked,
  current Python environment or availability of Ruff. Add non-repairing lock and
  exact environment freshness checks using the selected environment. Missing,
  stale and synchronized fixtures must respectively fail, fail and pass without
  modifying dependencies, locks or contracts. Setup alone prepares dependencies.

Bounded portability amendment supporting BDS-02 CI: support the native Android
producer on Linux x86_64 as well as the existing macOS host. Resolve the NDK host
tool directory and host bindgen library suffix explicitly; reject unsupported
hosts with actionable errors. Preserve target ABI mappings and macOS behavior.
Do not add Windows support, change mobile minimum OS versions or acquire runners.
Record Linux execution separately from command-construction tests on macOS.

## Checkpoint record

- BDS-01.01, commit `2030bcb`: the cohort identity now normalizes
  `CARGO_PROFILE_RELEASE_OPT_LEVEL` (unset equals `3`, unsupported values are
  rejected) and the iOS deployment target (an equivalent form is stable, a conflict
  is rejected), and includes release/target/SDK/deployment inputs. The identity
  schema advanced to 2, so older cohorts are not silently reused. The regression
  fixtures assert a changed profile changes the cohort location and equivalent
  inputs stay stable.
- BDS-01.02, commit `127bc05`: `native.verify` excludes only the cohort-root
  `manifest.json`; nested files with that basename are ordinary outputs. Fixtures
  reproduce the two native integrity defects: nested-manifest tampering/deletion and
  an inconsistent deployment target. Missing manifests and incompatible cohort
  schemas fail explicitly; byte-change, unexpected-file and symlink checks remain.
- BDS-01.03, commit `6080be2`: native UI builds select the framework path and Gradle
  task from the requested configuration (debug/release) and SDK (simulator/device).
  `make build-release-ios`, `make build-ios-device` and `make build-release-android`
  exist and are documented.
- BDS-01.04, commit `7bf20fc`: `check_tools` preflights the pinned Python environment
  and prints the setup command instead of repairing it. `make check-ios` runs the
  documented path to completion in a prepared environment.

Verification on 2026-09-28 (all exit 0), from the Branch project directory:

| Command | Result |
| --- | --- |
| `pytest tools/native-build/tests` | 28 passed, including 5 native identity and 5 manifest integrity cases |
| `make build-android` | Android debug app and androidTest compiled |
| `make build-release-android` | Android release app compiled, unsigned |
| `make build-ios` | iOS debug simulator framework and app compiled |
| `make build-release-ios` | iOS Release simulator framework and app compiled |
| `make build-ios-device` | iOS Release device framework and app compiled, unsigned |
| `make check-ios` / `make check-android` | checks passed |

Toolchain: rustc 1.98.0, Xcode 26.6 (17F113), iOS simulator SDK 26.5, JDK 21,
Android SDK platform android-36, build-tools 36.0.0, NDK 29.0.14206865. `IPHONEOS`
and release overrides were exercised through fixtures; no physical device was used.

### Corrective checkpoint record (2026-09-29)

BDS-01.01, commit `beefd3d`: cohort identity now records a bounded effective-input
set (compiler, wrapper, flag and per-target linker variables plus an existing
`.cargo/config.toml`). `CARGO_PROFILE_RELEASE_OPT_LEVEL` stays the only supported
release-profile override; other `CARGO_PROFILE_RELEASE_*` overrides are rejected
before cache lookup. Output/cache paths (`CARGO_TARGET_DIR`, `BRANCH_BUILD_DIR`,
`BRANCH_NATIVE`) are not semantic inputs. Identity and subprocess execution share
the validated policy.

BDS-01.03, commit `eaf92a5`: action-aware CLI routing rejects unsupported options
and non-debug Android test requests before building; the native Android producer
resolves the NDK host toolchain tag and host bindgen library suffix explicitly and
rejects unsupported hosts. BDS-01.04, commit `7d3ca29`: checks verify lock freshness
and exact direct-dependency versions (including Ruff) without repair.

Verification on 2026-09-29 (Branch project directory, all exit 0):

| Command | Result |
| --- | --- |
| `pytest tools/native-build/tests` | 78 passed (identity, routing, environment cases) |
| `make verify-rust` | five Rust unit tests passed |
| `make build-android`, `make build-release-android` | compiled; Android native cohort verified |
| `make build-ios`, `make build-release-ios`, `make build-ios-device` | compiled |
| `make check-android`, `make check-ios` | ktlint, Android Lint, swift-format and Python checks passed |
| `branch-native env-check` | Python tool environment synchronized with the lockfile |

`make check-tools` now performs `uv lock --check`, `uv sync --check` and the exact
version preflight. The Linux producer path is covered by `test_routing` host-tag
cases and the macOS host build; it is not executed on Linux in this batch.

### Second corrective checkpoint record (2026-09-29)

BDS-01.01: one effective-input resolver now rejects `CARGO_BUILD_RUSTC`,
`CARGO_BUILD_RUSTC_WRAPPER`, `CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER`,
`CARGO_BUILD_TARGET` and `CARGO_INCREMENTAL` before cache lookup, resolves
`RUSTC`/`RUSTC_WRAPPER`/`RUSTC_WORKSPACE_WRAPPER` to the real executable behind
the selection, and evaluates repository, ancestor and selected Cargo-home
configuration. Only the `build`, `profile`, `target` and `env` Cargo tables
participate; credential, registry and alias tables are excluded and never
copied. Unsupported `build.rustc`/`build.rustc-wrapper`/`build.target`/
`build.incremental` and any `profile.release` setting are rejected. The Android
producer records the NDK-selected linkers in identity from the same resolver used
for subprocess construction, and a mismatched NDK host prebuilt directory now
fails instead of falling back to another host's directory.

Verification (Branch project directory, `cargo extbuild run --` router, exit 0):

| Command | Result |
| --- | --- |
| `pytest tools/native-build/tests` | 98 passed; added alias-rejection, real-executable resolution, ancestor/Cargo-home config, credential-exclusion and NDK-host mismatch cases |
| `ruff check` / `ruff format --check tools/native-build` | clean |

Cohort locations change because the identity now includes the Cargo configuration
and producer linkers; existing cohorts are not silently reused. No Linux producer
execution is claimed.

## Sequence

[BDS-00](bds-00-contracts.md) · [BDS-01](bds-01-native-build.md) · [BDS-02](bds-02-shared-hosts.md) · [BDS-03](bds-03-theme.md) · [BDS-04](bds-04-primitives.md) · [BDS-05](bds-05-navigation.md) · [BDS-06](bds-06-glass.md) · [BDS-07](bds-07-editing.md) · [BDS-08](bds-08-controls.md) · [BDS-09](bds-09-patterns.md) · [BDS-10](bds-10-platform.md) · [BDS-11](bds-11-media.md) · [BDS-12](bds-12-simulator-qualification.md) · [BDS-13](bds-13-device-qualification.md)
