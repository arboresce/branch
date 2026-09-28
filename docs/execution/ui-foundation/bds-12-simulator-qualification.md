# BDS-12: Complete simulator foundation qualification

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-01, BUI-02, BUI-03, BUI-04, BUI-05, BUI-06, BUI-07, BUI-08, BUI-09, BUI-10, BUI-11, BUI-12.
Prerequisites: [BDS-08](bds-08-controls.md), [BDS-09](bds-09-patterns.md), [BDS-11](bds-11-media.md).
Next action: inspect current authority and working-tree state, then execute BDS-12.01 after prerequisites are verified.

## Scope

- `docs/execution/ui-foundation/**`
- `docs/development/**`
- `contracts/ui-components.json`
- `contracts/platform-services.json`
- `app/** (bounded defects discovered by qualification)`
- `tools/native-build/** (qualification only)`
- `.github/workflows/**`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

No new component export is owned by this unit.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-12.01 | planned | Close inventory and API compatibility | V0, V2, V6 |
| BDS-12.02 | planned | Qualify accessibility and localization | V3, V4 |
| BDS-12.03 | planned | Qualify visual parity harness | V3, V4 |
| BDS-12.04 | planned | Reproduce builds and full workflows | V1, V2, V3, V6 |
| BDS-12.05 | planned | Issue simulator qualification record | V0, V4, V6 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-12.01: Close inventory and API compatibility

Scope: Audit all 92 exports and ten adapters against contracts, usage, states, semantics and actual tests; exercise a second consumer.

Definition of green: Every row names implementation and evidence; no catalog dependency reaches production; API boundary regressions are resolved.

Verify lane: V0, V2, V6. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-12.02: Qualify accessibility and localization

Scope: Run English/long/RTL, large-text, focus, contrast and available screen-reader/preference checks across risk-based combinations.

Definition of green: Simulator-supported accessibility cases pass; unsupported hardware observations stay explicit rather than waived.

Verify lane: V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-12.03: Qualify visual parity harness

Scope: Record paired baselines with deterministic clocks/assets and approved narrow masks/tolerances; inject known regressions.

Definition of green: Geometry/color/font changes are detected; matching logical frames/themes/scales/profiles pass without broad masking.

Verify lane: V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-12.04: Reproduce builds and full workflows

Scope: Use independent public context and documented commands to run both hosts, all three workflows, Rust/native regressions and CI-equivalent commands.

Definition of green: Nonzero suites and real runtime smoke tests pass; selected resources/configurations match; source stays independent of other checkouts.

Verify lane: V1, V2, V3, V6. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-12.05: Issue simulator qualification record

Scope: Reconcile all finding/requirement/component/service evidence and publish a portable local evidence index.

Definition of green: Status is simulator-qualified only; BDS-13 remains open with exact physical gaps; no device/store/production claim is inferred.

Verify lane: V0, V4, V6. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

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

