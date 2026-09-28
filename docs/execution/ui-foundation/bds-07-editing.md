# BDS-07: Editing, dialogs and sheet workflow

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-05, BUI-07, BUI-10.
Prerequisites: [BDS-05](bds-05-navigation.md).
Next action: inspect current authority and working-tree state, then execute BDS-07.01 after prerequisites are verified.

## Scope

- `app/ui/design-system/** (input/form/dialog/sheet)`
- `app/ui/patterns/** (modal host)`
- `app/catalog/**`
- `app/shared/app/** (presentation owner)`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

C048 AppTextField; C049 AppPasswordField; C050 AppTextArea; C051 AppSearchField; C052 AppSelectField; C053 AppCodeField; C057 AppFormField; C058 AppFieldLabel; C059 AppSupportingText; C060 AppValidationMessage; C066 AppDialog; C067 AppAlertDialog; C068 AppConfirmationDialog; C069 AppModalBottomSheet; C089 AppModalHost.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-07.01 | planned | Implement framework-backed editors | V2, V3, V4 |
| BDS-07.02 | planned | Implement selection and code fields | V2, V3, V4 |
| BDS-07.03 | planned | Implement form semantics | V2, V3, V4 |
| BDS-07.04 | planned | Implement controlled dialogs, sheets and modal host | V2, V3, V4 |
| BDS-07.05 | planned | Qualify FLOW-02 | V3, V4 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-07.01: Implement framework-backed editors

Scope: Implement C048–C051 without losing selection/composing state, secure input or IME options.

Definition of green: Typing/composition/paste/delete, read-only versus disabled, focus and secure masking have actual target evidence.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-07.02: Implement selection and code fields

Scope: Implement C052–C053 with controlled selections and constrained code input.

Definition of green: Cancel differs from confirmation; paste/backspace and accessibility work; codes never enter disk restoration or evidence.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-07.03: Implement form semantics

Scope: Implement C057–C060 with labels, supporting text and validation association.

Definition of green: Errors are announced meaningfully; large text reflows; required/invalid/read-only states remain distinct.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-07.04: Implement controlled dialogs, sheets and modal host

Scope: Implement C066–C069 and C089 with one layering/focus owner and distinct dismiss intents.

Definition of green: Back/outside/drag/cancel/confirm paths follow policy; focus returns correctly; modal host does not own a second navigation stack.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-07.05: Qualify FLOW-02

Scope: Exercise dirty editing with a lower field, keyboard, validation, cancelled dismissal and exactly-once save.

Definition of green: Both simulators complete the flow; pending-save cancellation and duplicate activation are covered; no form draft is written to disk.

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

