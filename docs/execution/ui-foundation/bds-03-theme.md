# BDS-03: Tokens, resources and appearance

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-04, BUI-09.
Prerequisites: [BDS-02](bds-02-shared-hosts.md).
Next action: inspect current authority and working-tree state, then execute BDS-03.01 after prerequisites are verified.

## Scope

- `app/ui/design-system/**`
- `app/platform/** (appearance/accessibility)`
- `app/shared/app/** (preference injection)`
- `app/shared/xc-framework/** (resource integration)`
- `app/ios/project.yml`
- `app/catalog/**`
- `docs/spec/ui-foundation.md`
- `docs/development/**`
- `app/gradle/libs.versions.toml and dependency metadata`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

Resource prerequisite: reviewed, complete, committed consumer resources and public-safe notices. Ordinary builds remain independent; never add a dependency on an unpublished asset source or another checkout.

## Assigned inventory

C001 AppTheme.

OS10 AccessibilityPreferencesProvider.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-03.01 | planned | Accept self-contained resource bundle | V0, V2, V3, V6 |
| BDS-03.02 | planned | Complete semantic tokens and numeric decisions | V0, V2, V4 |
| BDS-03.03 | planned | Implement AppTheme and reactive preferences | V2, V3 |
| BDS-03.04 | planned | Observe actual accessibility signals | V2, V3, V4 |
| BDS-03.05 | planned | Qualify shared typography and appearance | V3, V4 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-03.01: Accept self-contained resource bundle

Scope: Declare exact committed consumer paths for typed tokens, font files, vectors and notices; verify resource identities and standalone use.

Definition of green: Resources need no other checkout/tooling during ordinary builds; same pinned font/version/weights and glyph coverage reach both applications.

Verify lane: V0, V2, V3, V6. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-03.02: Complete semantic tokens and numeric decisions

Scope: Implement complete light/dark/increased-contrast role sets, dimensions, typography weights and reading-width/motion choices; record exact values and provisional limits.

Consume the maintained typed values and record the resolved visual contract.
Do not create independently editable literals in the public theme. Any required
resource correction uses the reviewed maintainer update process before the
consumer gate is closed; consumers keep working from committed resources.

Definition of green: Alias/type/mode checks and contrast pairs pass; no duplicated editable palettes or unrecorded component literals; fonts do not synthesize divergent weights.

Verify lane: V0, V2, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-03.03: Implement AppTheme and reactive preferences

Scope: Implement C001 with System/Light/Dark, explicit override precedence, shared metrics and local theme/effects preference storage under approved policy.

Definition of green: System changes update live UI; explicit modes win; corrupt preferences recover safely; requested effects cannot defeat accessibility/capability restrictions.

Verify lane: V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-03.04: Observe actual accessibility signals

Scope: Implement OS10 early with known/unknown capabilities, observer disposal, text scale, contrast/motion/transparency inputs and safe injected test values.

Definition of green: Simulated/system changes reach policy without invented signals; disposal and unknown-signal behavior are tested on both targets.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-03.05: Qualify shared typography and appearance

Scope: Exercise font resources, English, long and RTL fixtures, large text and all theme modes in catalog and diagnostic.

Definition of green: Paired captures and resource tests identify exact assets; no missing glyphs in required fixtures; contrast failures are corrected before closing theme gate.

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
