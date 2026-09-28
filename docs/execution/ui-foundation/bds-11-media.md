# BDS-11: Image loading and media workflow

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-05, BUI-08, BUI-09, BUI-10.
Prerequisites: [BDS-06](bds-06-glass.md), [BDS-09](bds-09-patterns.md), [BDS-10](bds-10-platform.md).
Next action: inspect current authority and working-tree state, then execute BDS-11.01 after prerequisites are verified.

## Scope

- `app/ui/patterns/** (image wrapper)`
- `app/catalog/**`
- `app/shared/app/** (fixture assembly only)`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

C092 AppAsyncImage.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-11.01 | planned | Implement C092 image loading boundary | V2, V3, V4 |
| BDS-11.02 | planned | Assemble FLOW-03 | V3, V4 |
| BDS-11.03 | planned | Exercise media lifecycle and effects | V3, V4 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-11.01: Implement C092 image loading boundary

Scope: Wrap compatible Coil with size-aware loading, caller descriptions, placeholders, errors and deterministic fakes.

Definition of green: Cancellation, decoded-size bounds, cache reuse and failed loads pass without real-network unit dependencies.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-11.02: Assemble FLOW-03

Scope: Combine fixed imagery, floating controls, picker/share adapters and effects profiles without a video-player product.

Definition of green: Selection/cancel/share launch and slider/toggle actions work on both simulators; fixtures stay outside production.

Verify lane: V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-11.03: Exercise media lifecycle and effects

Scope: Move backgrounds and switch profiles, then background/resume and remove sources.

Definition of green: No stale callbacks, leaked content handles/captures or swallowed gestures; device performance remains pending.

Verify lane: V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

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

