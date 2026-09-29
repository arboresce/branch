# BDS-00: Contracts and baseline

Status: correction required after independent review, 2026-09-29.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-12, BUI-01, BUI-02.
Prerequisites: None; first execution unit.
Next action: correct BDS-00.02 under the review amendment below; retain the accepted mapping and historical baseline.

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
- `tools/native-build/src/branch_native_build/inventory.py`
- `tools/native-build/src/branch_native_build/cli.py (contract-check routing only)`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

No new component export is owned by this unit.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-00.01 | complete | Approve public contract mapping | V0 |
| BDS-00.02 | planned | Correct inventory authority validation | V0, V1 |
| BDS-00.03 | complete | Record actual baseline and historical context | V0, V1, V6 |

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

Checkpoint evidence: submitted commits `0d06e44`, `2e1d29e`, `c0ebef4`; BDS-00.02 is reopened.
Current implementation slice: none.
Open failures/limits: F07 below; corrected implementation requires independent acceptance.

## Review amendment (2026-09-29)

F07: `inventory._known` scans every mention of an identifier. An inventory entry
assigned to an undefined checkpoint passes if the same identifier is added as
incidental prose in any plan. This does not establish an owning slice.

BDS-00.02 must resolve authoritative checkpoint table rows and matching scope,
green-criteria and verification definitions, and requirement section definitions.
Reject orphan mentions, duplicate definitions, table/section disagreement,
missing owners and broken repository-local authority/plan links. Keep the valid
92-component, ten-service, 65-checkpoint mapping; do not count prose references
as additional checkpoints. Preserve closed schemas and existing rejection cases.
Use disposable fixtures to prove each rejection, including the observed orphan
mention case. Record actual evidence formats without claiming component behavior
is implemented merely because the inventory passes.

The mapping and historical baseline are retained. This correction changes the
validator, not the approved component inventory or downstream scope.

## Checkpoint record

All commands ran from the Branch project directory. `cargo extbuild run --` is the
workstation build-output router and is not part of the repository command surface.

- BDS-00.01, commit `0d06e44`: adopted the approved specification, the 92-entry
  component inventory, the ten-entry service inventory and the fourteen checkpoint
  plans; reconciled module ownership, exclusions and persistence in
  `docs/architecture.md`.
- BDS-00.02, commit `2e1d29e`: added closed schemas `contracts/schemas/ui-components.json`
  and `contracts/schemas/platform-services.json` and the `branch-native contract-check`
  validator. `make test-shared` is unrelated; the governing checks are
  `branch-native contract-check` and the Python package tests.
- BDS-00.03, commit `c0ebef4`: recorded the 2026-09-28 baseline in
  `docs/execution/mobile-bootstrap-rcld.md` and separated historical bootstrap
  revisions from the current checkout.

Verification on 2026-09-28:

| Command | Result |
| --- | --- |
| `make verify-rust` | exit 0; five unit tests passed, zero failed |
| `branch-native config-check` | exit 0 |
| `branch-native contract-check` | exit 0; `{"checkpoints":65,"components":92,"requirements":12,"services":10}` |
| `uv run --project tools/native-build --locked --no-sync pytest tools/native-build/tests` | exit 0; 28 passed (12 inventory/contract cases) |
| `make check-ios` / `make check-android` | exit 0 |

Tooling: rustc/cargo 1.98.0, uv 0.12.19, Python 3.14.7, ruff 0.16.6, pytest 9.1.1,
Xcode 26.6, JDK 21. No whole-checkout qualification is claimed.

## Sequence

[BDS-00](bds-00-contracts.md) · [BDS-01](bds-01-native-build.md) · [BDS-02](bds-02-shared-hosts.md) · [BDS-03](bds-03-theme.md) · [BDS-04](bds-04-primitives.md) · [BDS-05](bds-05-navigation.md) · [BDS-06](bds-06-glass.md) · [BDS-07](bds-07-editing.md) · [BDS-08](bds-08-controls.md) · [BDS-09](bds-09-patterns.md) · [BDS-10](bds-10-platform.md) · [BDS-11](bds-11-media.md) · [BDS-12](bds-12-simulator-qualification.md) · [BDS-13](bds-13-device-qualification.md)
