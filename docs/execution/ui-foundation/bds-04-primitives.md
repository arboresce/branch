# BDS-04: Essential components and scaffolds

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-05, BUI-07.
Prerequisites: [BDS-03](bds-03-theme.md).
Next action: inspect current authority and working-tree state, then execute BDS-04.01 after prerequisites are verified.

## Scope

- `app/ui/design-system/**`
- `app/ui/patterns/**`
- `app/catalog/**`
- `app/ui/diagnostic/public/**`
- `docs/development/ui-components.md (new)`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

C002 AppSurface; C003 AppCard; C004 AppDivider; C005 AppScrim; C006 AppText; C007 AppLabel; C008 AppIcon; C009 AppImage; C010 AppAvatar; C011 AppBadge; C029 AppButton; C030 AppIconButton; C031 AppIconToggleButton; C032 AppFloatingActionButton; C033 AppExtendedFloatingActionButton; C077 AppScreenScaffold; C078 AppScreenHeader; C079 AppFormScaffold.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-04.01 | planned | Surfaces and separation | V2, V3, V4 |
| BDS-04.02 | planned | Text, labels and icons | V2, V3, V4 |
| BDS-04.03 | planned | Images, avatars and badges | V2, V3, V4 |
| BDS-04.04 | planned | Core action controls | V2, V3, V4 |
| BDS-04.05 | planned | Floating actions | V2, V3, V4 |
| BDS-04.06 | planned | Screen/form scaffolds and diagnostic consumption | V2, V3, V4 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-04.01: Surfaces and separation

Scope: Implement C002–C005 with theme roles and readable clipping/layering.

Definition of green: Surface/card/divider/scrim variants, semantics and visual states have meaningful tests and paired samples.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-04.02: Text, labels and icons

Scope: Implement C006–C008 with role typography, semantic labels, decorative icon behavior and RTL handling.

Definition of green: Scaling, overflow, descriptions and directional icons pass; labels associate correctly without duplicated announcements.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-04.03: Images, avatars and badges

Scope: Implement C009–C011 with sizing, description, fallback and count rules.

Definition of green: Missing content, aspect ratio, long/count overflow and decorative/meaningful semantics are covered.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-04.04: Core action controls

Scope: Implement C029–C031 with value/callback semantics, loading suppression and focus states.

Definition of green: Repeated activation while busy is suppressed; toggle state, disabled state and accessible labels are correct.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-04.05: Floating actions

Scope: Implement C032–C033 with minimum targets and expanding content.

Definition of green: Large text and extended labels remain operable; press/loading/disabled behavior matches ordinary actions.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-04.06: Screen/form scaffolds and diagnostic consumption

Scope: Implement C077–C079 with one inset owner; migrate diagnostic styling to public shared APIs. Qualify the catalog's native viewport before approving geometry samples, including its iOS launch/scene metadata relative to the production host.

Definition of green: System/keyboard/overlay inset tests pass without double padding; runtime snapshot remains selectable and scrollable. Measure actual window/content/safe-area bounds and resolve unintended compatibility framing or clipped catalog content rather than masking it in screenshots. The initial iOS probe capture's large black margins are not an approved screen baseline; its built plist lacks launch/scene keys present in production, which is a starting point for diagnosis rather than a measured root-cause conclusion.

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
