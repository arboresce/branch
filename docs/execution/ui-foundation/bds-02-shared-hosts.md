# BDS-02: Reactive shared hosts and verification harness

Status: correction required after independent review, 2026-09-29.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-02, BUI-03, BUI-10, BUI-11.
Prerequisites: [BDS-01](bds-01-native-build.md).
Next action: after corrected BDS-00/01 gates, complete BDS-02.02 through BDS-02.05 under the review amendment below, then stop for independent acceptance before BDS-03.

## Scope

- `app/settings.gradle.kts`
- `app/gradle/libs.versions.toml and dependency locks/verification metadata`
- `app/shared/app/** (new)`
- `app/shared/xc-framework/**`
- `app/ui/diagnostic/public/**`
- `app/android/app/**`
- `app/ios/App/**`
- `app/ios/Runtime/**`
- `app/ios/Tests/**`
- `app/ios/UITests/**`
- `app/catalog/** (new)`
- `app/platform/** (interfaces only)`
- `app/ui/design-system/** (resource probe only)`
- `app/ui/patterns/** (skeleton only)`
- `scripts/commands.sh`
- `Makefile`
- `.github/workflows/** (new, repository checks only)`
- `app/catalog/android/** (development application host)`
- `app/catalog/ios/** (development application host and tests)`
- `app/catalog/xc-framework/** (development-only framework bridge)`
- `tools/native-build/src/branch_native_build/mobile.py`
- `tools/native-build/src/branch_native_build/cli.py`
- `tools/native-build/tests/ (catalog, runner and resource routing)`
- `contracts/development.toml and its schema (explicit CI simulator/emulator selection)`
- `docs/development/`
- `docs/execution/ui-foundation/ (this amendment and evidence only)`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

No new component export is owned by this unit.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-02.01 | complete | Introduce compiling module boundaries | V0, V2 |
| BDS-02.02 | planned | Correct reactive lifecycle and in-flight races | V2, V3 |
| BDS-02.03 | planned | Launch the independent deterministic catalog | V2, V3 |
| BDS-02.04 | planned | Run the required dependency prototypes | V2, V3 |
| BDS-02.05 | planned | Complete shared runners and viable CI bootstrap | V0, V2, V3 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-02.01: Introduce compiling module boundaries

Scope: Register minimal shared application, design-system, patterns, platform and catalog modules using existing target/identity conventions.

Definition of green: Android and iOS compile; hosts remain thin; production dependency graph excludes catalog.

Verify lane: V0, V2. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-02.02: Make runtime presentation reactive

Scope: Add a stable iOS controller/update surface and common loading/error/content presentation; preserve native runtime ownership and off-main-thread calls.

Definition of green: Successive updates reach the existing controller; cancellation/disposal suppress stale results; real runtime diagnostic still renders.

Verify lane: V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-02.03: Build deterministic catalog foundations

Scope: Provide independent development launch, synthetic lists/forms/media, controlled clocks and runtime/service fakes.

Definition of green: Catalog and real app are separate consumers; fixture identity/data cannot appear in production through a dependency.

Verify lane: V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-02.04: Prove risky dependencies and resource delivery

Scope: Compile small Navigation 3, Backdrop, Coil and shared resource prototypes against a pinned compatible set; determine actual test task names.

Definition of green: Both hosts load a shared resource; prototypes compile/run on both simulators or produce a bounded incompatibility decision before component investment.

Verify lane: V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-02.05: Wire actual test runners and CI commands

Scope: Enable shared tests and Android/iOS target runners; expose documented commands and CI configuration using public dependencies.

Definition of green: Nonzero shared and target tests run; CI definitions name real commands; unavailable hosted runners are recorded separately from local evidence.

Verify lane: V0, V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

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

Checkpoint evidence: submitted commits `4b375b9`, `8cdf503`, `2220f66`, `cbd964e`, `1366b41`, `8eb825f`; BDS-02.02 through BDS-02.05 are reopened.
Current implementation slice: none.
Open failures/limits: F02 through F06 below; hosted CI runners remain unexecuted.

## Review amendment (2026-09-29)

This amendment supersedes the submitted completion and dependency-deferral claims
below. Keep those receipts as historical implementation evidence. BDS-02.01's
module skeletons are retained; they do not prove launchable reuse or dependency
compatibility. Correct all reopened checkpoints before independent acceptance.

- F02 / BDS-02.02: serialize controller state and native work. A cancelled old job
  currently clears the shared active flag after a newer load starts; disposal is
  merely cancellation and still allows future loads. The factory-owned MainScope
  is used by the real iOS host, not only the catalog. Implement the terminal
  disposal and retry policy in BUI-03. Wire host removal, foreground/background
  cancellation and catalog composition disposal explicitly, without shutting
  down a native handle while a blocking call still uses it. Preserve the existing
  Rust facade. Use controlled in-flight work to test cancel/restart, old cleanup,
  duplicate load, failure/retry, disposal and attempted post-disposal load. Tests
  that call the internal result method directly are not sufficient. Both hosts
  must visibly render successive updates through the same controller/view and
  retain the real Rust snapshot smoke tests. Add coroutines test support through
  pinned dependencies where required.
- F03 / BDS-02.03: CatalogRoot is currently unreachable from any application host.
  Add independent Android and iOS development hosts with identities
  `ai.arboresce.branch.catalog`, separate output/installation paths and a
  development-only iOS bridge. Document real launch/test commands. Both must
  render CatalogRoot and fixed fixtures; production app/framework dependency
  graphs and artifacts must exclude catalog code and fixtures. Do not add a
  production debug switch or change the production identity. Retain the existing
  synthetic fixtures and fixed clock, adding bounded controllable work as needed.
- F04 / BDS-02.04: no Navigation 3, Backdrop or Coil prototype was implemented.
  Their deferral is rejected. Resolve and lock compatible versions of these
  already-approved libraries against the current toolchain, verify actual APIs,
  and run small catalog probes on both simulators. Demonstrate a two-entry
  navigation transition and iOS serialization; a library-neutral internal glass
  adapter with opaque fallback; and a local deterministic image success/error
  case. Preserve API 28 and iOS 18. These probes do not implement the later
  complete components or workflows. Exact compatible patch versions are an
  implementation choice within this fixed library set. Replacement libraries,
  minimum OS/toolchain changes or deferral require a new review decision; report
  concrete incompatibility evidence and continue independent corrections first.
- F06 / BDS-02.05: shared tests currently execute only on iOS; Android KMP test
  compilations are not enabled. Enable the actual Android shared-test runner and
  keep the iOS runner, with platform-specific documented commands and CI jobs.
  Identify all shared modules declaring common tests and fail when any lacks a
  required runner or has zero executed tests. Record nonzero counts per module
  and target; force execution for batch acceptance rather than counting cached
  Gradle tasks as fresh tests. Keep host instrumentation/XCTest lanes distinct.
- F05 / BDS-02.05: the Linux Android job invokes a producer with hardcoded Darwin
  NDK paths and a `.dylib` host library. Apply the BDS-01 portability amendment.
  Provision uv/Python, JDK 21, Android command-line tools/SDK/NDK and selected
  Xcode/simulator explicitly, with one selected Python environment across setup
  and checks. Use a compatible macOS ARM64 runner for iOS and Linux x86_64 for
  Android; explicitly pass the emulator selected by the CI runner to the test
  command. Retain local simulator defaults, using a validated CI override when
  the local runtime is absent. Validate workflow structure and command/tool
  preconditions without claiming hosted execution or creating external runs.

Resource decision: retain the working external-build aggregation/copy approach
for this batch; a framework integration migration is not required. Derive copy
destinations from the selected Xcode product, bound destructive copying to that
resource directory, and test Debug/Release simulator plus unsigned device
packaging with a missing-resource rejection. Scope and document the app-target
script-sandbox exception; do not assume it proves a resource failure or enable
unrelated exceptions. Shared resource changes in the dependency probes must
remain visible on both hosts. Full brand/font/icon assets still belong to BDS-03.

Execution policy: complete all independent corrections in this authorized batch,
update evidence and stop before BDS-03. An incompatibility blocks its own dependent
work; it does not waive the requirement or justify skipping other runnable fixes.
Scope/library replacements and acceptance decisions remain with the reviewer.

## Checkpoint record

- BDS-02.01, commit `4b375b9`: registered `:ui:design-system`, `:ui:patterns`,
  `:platform`, `:shared:app` and `:catalog` with committed locks. The Android and iOS
  hosts consume the shared application module; the boundary test proves no production
  module depends on `:catalog`.
- BDS-02.02, commit `8cdf503`: added typed `DiagnosticPhase` loading/error/content
  presentation, a stable `RuntimeController` with stale/cancellation suppression and
  retry, and host wiring that updates observable state instead of recreating the tree.
- BDS-02.03, commit `2220f66`: catalog fixtures with namespaced identifiers, a fixed
  clock and a scripted runtime source; the catalog is an independent consumer of the
  shared modules and is excluded from production.
- BDS-02.04, commits `cbd964e` and `1366b41`: shared Compose string resources in the
  diagnostic module, consumed by the loading and retry presentation. Android merges
  the resources into app assets; iOS copies the aggregated framework resource bundle
  into the app bundle. The first commit did not package the iOS bundle, so `1366b41`
  corrects the iOS resource delivery and the two together are the verified checkpoint.
- BDS-02.05, commit `8eb825f`: `make test-shared` runs `:shared:app:allTests` and
  `:catalog:allTests`; `.github/workflows/branch-checks.yml` names the real Rust,
  tools, Apple and Android commands. The pinned Gradle test task names are
  `iosSimulatorArm64Test` and the aggregated `allTests`; the target runners are
  `xcodebuild test` (`make test-ios`) and `connectedDebugAndroidTest`
  (`make test-android`).

Submitted dependency deferrals (rejected by the review amendment above):

- Navigation 3: compatible KMP artifacts 1.1.1 were observed in the local Gradle
  cache, but the Navigation 3 API is not pinned until BDS-05 owns the navigation and
  serialization requirements.
- Backdrop: no approved pinned coordinate; BDS-06 owns the internal adapter and the
  recorded replacement decision.
- Coil: not resolved in this slice; BDS-11 owns the media dependency set and its
  compatibility evidence.

Verification on 2026-09-28 (all exit 0), from the Branch project directory:

| Command | Result |
| --- | --- |
| `make test-shared` | 13 shared tests executed (8 `:shared:app`, 5 `:catalog`) |
| `make test-ios` | 4 XCTest cases passed (successive controller updates, sanitized error, native snapshot, UI snapshot) |
| `make test-android` | 3 instrumented tests passed on the API 36 arm64 emulator |
| `make check-ios` / `make check-android` | ktlint, swift-format and Android Lint passed |
| `make build-android` / `make build-ios` | both hosts compiled with the shared resources |
| `make build-release-ios` / `make build-ios-device` | Release simulator and device builds compiled with resources |

Resource evidence: the Android debug APK contains
`assets/composeResources/ai.arboresce.branch.ui.resources/values/strings.commonMain.cvr`;
the iOS debug app contains
`Branch.app/compose-resources/composeResources/ai.arboresce.branch.ui.resources/values/strings.commonMain.cvr`.
A missing iOS bundle previously raised `MissingResourceException`; the corrected
build renders the shared loading string and the UI test passes.

Hosted CI: `.github/workflows/branch-checks.yml` was added and inspected but not
executed on a hosted runner; only the local commands were executed.

## Sequence

[BDS-00](bds-00-contracts.md) · [BDS-01](bds-01-native-build.md) · [BDS-02](bds-02-shared-hosts.md) · [BDS-03](bds-03-theme.md) · [BDS-04](bds-04-primitives.md) · [BDS-05](bds-05-navigation.md) · [BDS-06](bds-06-glass.md) · [BDS-07](bds-07-editing.md) · [BDS-08](bds-08-controls.md) · [BDS-09](bds-09-patterns.md) · [BDS-10](bds-10-platform.md) · [BDS-11](bds-11-media.md) · [BDS-12](bds-12-simulator-qualification.md) · [BDS-13](bds-13-device-qualification.md)
