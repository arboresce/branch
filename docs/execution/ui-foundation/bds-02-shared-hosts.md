# BDS-02: Reactive shared hosts and verification harness

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-02, BUI-03, BUI-10, BUI-11.
Prerequisites: [BDS-01](bds-01-native-build.md).
Next action: inspect current authority and working-tree state, then execute BDS-02.01 after prerequisites are verified.

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

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

No new component export is owned by this unit.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-02.01 | planned | Introduce compiling module boundaries | V0, V2 |
| BDS-02.02 | planned | Make runtime presentation reactive | V2, V3 |
| BDS-02.03 | planned | Build deterministic catalog foundations | V2, V3 |
| BDS-02.04 | planned | Prove risky dependencies and resource delivery | V2, V3 |
| BDS-02.05 | planned | Wire actual test runners and CI commands | V0, V2, V3 |

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

Checkpoint evidence: none.
Current implementation slice: none.
Open failures/limits: implementation not started.

## Sequence

[BDS-00](bds-00-contracts.md) · [BDS-01](bds-01-native-build.md) · [BDS-02](bds-02-shared-hosts.md) · [BDS-03](bds-03-theme.md) · [BDS-04](bds-04-primitives.md) · [BDS-05](bds-05-navigation.md) · [BDS-06](bds-06-glass.md) · [BDS-07](bds-07-editing.md) · [BDS-08](bds-08-controls.md) · [BDS-09](bds-09-patterns.md) · [BDS-10](bds-10-platform.md) · [BDS-11](bds-11-media.md) · [BDS-12](bds-12-simulator-qualification.md) · [BDS-13](bds-13-device-qualification.md)

