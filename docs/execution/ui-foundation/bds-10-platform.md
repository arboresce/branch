# BDS-10: Platform services and lifecycle integration

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-09.
Prerequisites: [BDS-03](bds-03-theme.md), [BDS-07](bds-07-editing.md).
Next action: inspect current authority and working-tree state, then execute BDS-10.01 after prerequisites are verified.

## Scope

- `app/platform/**`
- `app/shared/app/** (service injection)`
- `app/android/app/** (lifecycle/permissions)`
- `app/ios/App/**`
- `app/ios/project.yml (required privacy metadata only)`
- `app/catalog/**`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

No new component export is owned by this unit.

OS01 ShareLauncher; OS02 PhotoPickerLauncher; OS03 DocumentPickerLauncher; OS04 CameraLauncher; OS05 BrowserLauncher; OS06 PermissionController; OS07 BiometricAuthenticator; OS08 HapticFeedback; OS09 ClipboardController.
OS10 is implemented early by BDS-03.04; this unit verifies its integration without creating a second owner.

## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-10.01 | planned | Service outcomes and ownership | V0, V2 |
| BDS-10.02 | planned | Share and browser | V2, V3 |
| BDS-10.03 | planned | Photo and document picking | V2, V3 |
| BDS-10.04 | planned | Camera and permission requests | V2, V3 |
| BDS-10.05 | planned | Biometrics, haptics and clipboard | V2, V3 |
| BDS-10.06 | planned | Adapter lifecycle and privacy audit | V0, V2, V3 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-10.01: Service outcomes and ownership

Scope: Define typed per-service guarantees, cancellation, request IDs and handle cleanup; review OS10 implemented in BDS-03.

Definition of green: No generic success implies unavailable platform guarantees; duplicate completion and disposed-host fixtures fail safely.

Verify lane: V0, V2. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-10.02: Share and browser

Scope: Implement OS01 and OS05 with safe content/scheme validation and truthful launch outcomes.

Definition of green: Supported simulator launch/cancel/failure paths pass; share launch is never reported as delivery.

Verify lane: V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-10.03: Photo and document picking

Scope: Implement OS02 and OS03 with opaque handles, bounded access and cleanup.

Definition of green: Selection/cancellation, access lifetime and unavailable fixtures pass; no blanket permission or assumed path is required.

Verify lane: V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-10.04: Camera and permission requests

Scope: Implement OS04 and OS06 with explicit user-triggered requests and temporary resource ownership.

Definition of green: Denied/restricted/unavailable/cancel paths pass; simulator hardware absence is explicit; no startup prompts or reprompt loops.

Verify lane: V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-10.05: Biometrics, haptics and clipboard

Scope: Implement OS07–OS09 respecting settings, sensitive content and actual platform guarantees.

Definition of green: No invented identity; no clipboard polling; unsupported haptics safe; simulator coverage and physical-only gaps are recorded separately.

Verify lane: V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-10.06: Adapter lifecycle and privacy audit

Scope: Exercise service completion racing cancellation/recreation; verify OS10 observer disposal and accurate metadata.

Definition of green: All ten adapters have target builds and supported simulator evidence; outstanding hardware rows are assigned to BDS-13.

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

