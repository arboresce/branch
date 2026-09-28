# BDS-08: Selection, pickers and remaining content controls

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-05, BUI-07.
Prerequisites: [BDS-07](bds-07-editing.md).
Next action: inspect current authority and working-tree state, then execute BDS-08.01 after prerequisites are verified.

## Scope

- `app/ui/design-system/** (selection/pickers/disclosure)`
- `app/catalog/**`
- `app/gradle/libs.versions.toml (date/time dependency only if justified)`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

C028 AppDisclosureGroup; C034 AppSwitch; C035 AppCheckbox; C036 AppTriStateCheckbox; C037 AppRadioButton; C038 AppRadioGroup; C039 AppSegmentedControl; C040 AppSegmentedControlItem; C041 AppFilterChip; C042 AppInputChip; C043 AppAssistChip; C044 AppSuggestionChip; C045 AppSlider; C046 AppRangeSlider; C047 AppStepper; C054 AppDatePicker; C055 AppDateRangePicker; C056 AppTimePicker.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-08.01 | planned | Selection groups | V2, V3, V4 |
| BDS-08.02 | planned | Chip families | V2, V3, V4 |
| BDS-08.03 | planned | Continuous and stepped values | V2, V3, V4 |
| BDS-08.04 | planned | Calendar and time pickers | V2, V3, V4 |
| BDS-08.05 | planned | Disclosure and remaining control inventory | V2, V3, V4 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-08.01: Selection groups

Scope: Implement C034–C040 with distinct switch/checkbox/radio/segment roles and caller-owned state.

Definition of green: Mixed checkbox, single-selection groups, disabled choices, labels, focus and non-gesture activation pass.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-08.02: Chip families

Scope: Implement C041–C044 with distinct selection, removal, assist and suggestion actions.

Definition of green: Removal does not double-trigger selection; long labels/disabled states and semantics pass.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-08.03: Continuous and stepped values

Scope: Implement C045–C047 with bounds, step/range policy and accessible alternatives.

Definition of green: Clamping, RTL mapping, discrete steps and disabled/keyboard/accessibility adjustment pass.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-08.04: Calendar and time pickers

Scope: Implement C054–C056 with explicit date-only/time types, constraints, draft confirmation and cancellation.

Definition of green: Leap days, month/year boundaries, ranges, locale formatting and cancel-without-commit pass.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-08.05: Disclosure and remaining control inventory

Scope: Implement C028 and reconcile C034–C056 variants with catalog coverage.

Definition of green: Expanded/collapsed semantics and nested focus pass; no silently missing variant in assigned component rows.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

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

