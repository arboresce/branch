# BDS-01: Native integrity and build profiles

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-01, BUI-02.
Prerequisites: [BDS-00](bds-00-contracts.md).
Next action: inspect current authority and working-tree state, then execute BDS-01.01 after prerequisites are verified.

## Scope

- `tools/native-build/src/branch_native_build/native.py`
- `tools/native-build/src/branch_native_build/config.py`
- `tools/native-build/src/branch_native_build/mobile.py`
- `tools/native-build/tests/`
- `contracts/native-artifacts.toml and its schema/settings projection`
- `app/ios/project.yml`
- `scripts/commands.sh`
- `Makefile`
- `docs/spec/native-artifacts.md`
- `docs/development/`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

No new component export is owned by this unit.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-01.01 | planned | Control effective native configuration | V1 |
| BDS-01.02 | planned | Close manifest integrity gap | V1 |
| BDS-01.03 | planned | Separate native UI build profiles | V1, V2 |
| BDS-01.04 | planned | Make environment setup reproducible | V1, V6 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-01.01: Control effective native configuration

Scope: Specify normalized/rejected build environment inputs and version identity; include supported overrides, targets, SDK/configuration and producer inputs without host secrets.

Definition of green: Profile override changes identity or fails; deployment-target mismatch cannot silently reuse a cohort; controlled equivalent inputs remain stable.

Verify lane: V1. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-01.02: Close manifest integrity gap

Scope: Exclude only the cohort-root metadata file; verify nested manifests and all declared outputs; retain symlink and stale-selection checks.

Definition of green: Nested-manifest tampering and unexpected nested files fail; normal manifest verification, missing-file and byte-change tests pass.

Verify lane: V1. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-01.03: Separate native UI build profiles

Scope: Select framework paths by SDK, target and configuration; add explicit simulator Release and future device build routing without store/signing assumptions.

Definition of green: Both simulator configurations consume correct frameworks/resources; device framework compiles where tooling permits; no false device-run claim.

Verify lane: V1, V2. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-01.04: Make environment setup reproducible

Scope: Prepare the selected locked Python environment; diagnose absent dependencies in checks; preserve existing Make behavior and documented external-output routing.

Definition of green: An independently prepared environment runs the documented check path; checks do not repair dependencies/contracts/locks.

Verify lane: V1, V6. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

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

