# BDS-13: Physical-device and final foundation qualification

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-08, BUI-09, BUI-11, BUI-12.
Prerequisites: [BDS-12](bds-12-simulator-qualification.md).
Next action: inspect current authority and working-tree state, then execute BDS-13.01 after prerequisites are verified.

## Scope

- `docs/execution/ui-foundation/**`
- `docs/development/**`
- `app/** (bounded hardware corrections)`
- `tools/native-build/** (device lanes)`
- `contracts/** (reviewed support/policy changes only)`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

External gate: physical Android and iPhone access is not currently available for this task. Keep V5 pending. Execute the Android and iOS device slices independently as hardware becomes available; neither may borrow simulator qualification.

## Assigned inventory

No new component export is owned by this unit.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-13.01 | planned | Qualify physical Android | V3, V4, V5 |
| BDS-13.02 | planned | Qualify physical iOS | V3, V4, V5 |
| BDS-13.03 | planned | Close full acceptance | V0, V5, V6 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. BDS-13.01 and BDS-13.02 each
depend on BDS-12 and their own device access; neither depends on the other.
BDS-13.03 depends on both physical checkpoints. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-13.01: Qualify physical Android

Scope: Select available representative Android hardware/OS and record release-build frame pacing, input, resources, accessibility and hardware services with effects on/off.

Definition of green: Actual device receipts meet recorded budgets; camera/haptics/biometric and relevant fallback paths are exercised; uncovered support classes remain identified.

Verify lane: V3, V4, V5. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-13.02: Qualify physical iOS

Scope: Arrange iPhone access and local device build/signing through existing secure mechanisms; run equivalent release/hardware checks.

Definition of green: Actual iPhone receipts cover framework/resources, lifecycle, effects, accessibility and OS services; simulator evidence is not substituted.

Verify lane: V3, V4, V5. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-13.03: Close full acceptance

Scope: Set evidence-backed device budgets and final effects policy, repair measured defects and reconcile full acceptance.

Definition of green: All required physical and simulator gates pass with supported configurations named; otherwise foundation remains explicitly partially qualified.

Verify lane: V0, V5, V6. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

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
Open failures/limits: implementation not started; both physical target gates pending.

## Sequence

[BDS-00](bds-00-contracts.md) · [BDS-01](bds-01-native-build.md) · [BDS-02](bds-02-shared-hosts.md) · [BDS-03](bds-03-theme.md) · [BDS-04](bds-04-primitives.md) · [BDS-05](bds-05-navigation.md) · [BDS-06](bds-06-glass.md) · [BDS-07](bds-07-editing.md) · [BDS-08](bds-08-controls.md) · [BDS-09](bds-09-patterns.md) · [BDS-10](bds-10-platform.md) · [BDS-11](bds-11-media.md) · [BDS-12](bds-12-simulator-qualification.md) · [BDS-13](bds-13-device-qualification.md)
