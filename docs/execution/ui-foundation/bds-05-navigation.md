# BDS-05: Navigation shell and list-detail workflow

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-06, BUI-10.
Prerequisites: [BDS-04](bds-04-primitives.md).
Next action: inspect current authority and working-tree state, then execute BDS-05.01 after prerequisites are verified.

## Scope

- `app/shared/app/**`
- `app/ui/design-system/** (navigation and initial list controls)`
- `app/platform/** (back/host integration)`
- `app/catalog/**`
- `app/android/app/**`
- `app/ios/App/**`
- `app/shared/xc-framework/**`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

C012 AppTopAppBar; C013 AppToolbar; C014 AppBottomActionBar; C015 AppTabBar; C016 AppTabBarItem; C017 AppTabRow; C018 AppTab; C019 AppNavigationRail; C020 AppBackButton; C021 AppCloseButton; C022 AppPageIndicator; C023 AppListItem; C024 AppNavigationListItem; C025 AppSection; C026 AppSectionHeader; C027 AppSectionFooter.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-05.01 | planned | Define common navigation owner and serializers | V2, V3 |
| BDS-05.02 | planned | Implement shared navigation chrome | V2, V3, V4 |
| BDS-05.03 | planned | Implement list-detail building blocks | V2, V3, V4 |
| BDS-05.04 | planned | Integrate reversible back and presentation lifetime | V2, V3 |
| BDS-05.05 | planned | Qualify FLOW-01 | V3, V4 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-05.01: Define common navigation owner and serializers

Scope: Implement typed routes, independent tab stacks, stable entry IDs and explicit iOS serializers with lightweight arguments.

Definition of green: Repeated route instances remain distinct; invalid serialization recovers safely; no competing host stack appears.

Verify lane: V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-05.02: Implement shared navigation chrome

Scope: Implement C012–C022 and bind caller-owned selected state to navigation requests.

Definition of green: Back/Up/Close distinctions, root protection, tabs/rail and disabled actions have tested semantics.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-05.03: Implement list-detail building blocks

Scope: Implement C023–C027 and entry-scoped scroll state for the first workflow.

Definition of green: Row actions, disclosure affordance, sections and stable lazy keys behave correctly under reuse and long labels.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-05.04: Integrate reversible back and presentation lifetime

Scope: Connect Android back and iOS gestures to one completion path; arbitrate horizontal content/sheet gestures.

Definition of green: Cancel leaves state intact; completion pops once; disposed entries cancel work; switching tabs does not dispose retained entries.

Verify lane: V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-05.05: Qualify FLOW-01

Scope: Run list/detail, tab switch/return, scroll retention, cancelled/completed back and width changes with deterministic fixtures.

Definition of green: Complete workflow passes on both simulators with captured states and actual serializer round trips.

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

