# BDS-00: Contracts and baseline

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-12, BUI-01, BUI-02.
Prerequisites: None; first execution unit.
Next action: inspect current authority and working-tree state, then execute BDS-00.01 after prerequisites are verified.

## Scope

- `docs/spec/ui-foundation.md`
- `contracts/ui-components.json`
- `contracts/platform-services.json`
- `contracts/schemas/ui-components.json (new)`
- `contracts/schemas/platform-services.json (new)`
- `docs/architecture.md`
- `docs/spec/runtime-state.md`
- `docs/spec/native-artifacts.md`
- `docs/execution/mobile-bootstrap-rcld.md`
- `docs/README.md`
- `tools/native-build/tests/ (contract validation only)`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

No new component export is owned by this unit.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-00.01 | planned | Approve public contract mapping | V0 |
| BDS-00.02 | planned | Make inventory checks executable | V0, V1 |
| BDS-00.03 | planned | Record actual baseline and historical context | V0, V1, V6 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-00.01: Approve public contract mapping

Scope: Reconcile BUI-01–BUI-12, component/service inventories, module ownership, exclusions and approved persistence with existing architecture; keep observed bootstrap separate from target design.

Definition of green: Every review finding has an owner; all 92 components and ten services have explicit required behavior and slice assignments.

Verify lane: V0. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-00.02: Make inventory checks executable

Scope: Add closed schemas and repository-owned validation for unique IDs, complete inventories, owning slices and local references; establish the evidence-row format.

Definition of green: Missing/duplicate component, invalid owner, undeclared field and broken reference fixtures fail; valid contracts pass.

Verify lane: V0, V1. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-00.03: Record actual baseline and historical context

Scope: Run owning baseline checks, record environments and native cohorts, and clarify historical bootstrap revision scope without rewriting old receipts. Resolve exact new command categories before later slices.

Definition of green: Real baseline receipts exist for Rust/native and both host checks; pre-existing failures have impact bounds; no historical check is presented as fresh.

Verify lane: V0, V1, V6. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

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

