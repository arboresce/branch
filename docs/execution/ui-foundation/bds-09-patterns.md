# BDS-09: Async patterns, adaptation and restoration

Status: planned; no implementation checkpoint is complete.
Owner: Branch. Approved target: [UI Foundation v1](../../spec/ui-foundation.md).
Requirements: BUI-05, BUI-06, BUI-07.
Prerequisites: [BDS-07](bds-07-editing.md), [BDS-08](bds-08-controls.md).
Next action: inspect current authority and working-tree state, then execute BDS-09.01 after prerequisites are verified.

## Scope

- `app/ui/patterns/**`
- `app/ui/design-system/** (menus/feedback)`
- `app/shared/app/** (restoration, links and async fixtures)`
- `app/platform/** (minimal host saved state)`
- `app/catalog/**`

Only change these bounded areas for this unit. A needed expansion requires an
explicit scope amendment before editing. Preserve unrelated work and native identities.

## Assigned inventory

C061 AppDropdownMenu; C062 AppDropdownMenuItem; C063 AppContextMenu; C064 AppPopover; C065 AppTooltip; C070 AppCircularProgressIndicator; C071 AppLinearProgressIndicator; C072 AppSkeleton; C073 AppBanner; C074 AppSnackbar; C080 AppListDetailLayout; C081 AppAsyncContent; C082 AppLoadingState; C083 AppEmptyState; C084 AppErrorState; C085 AppOfflineState; C086 AppPullToRefresh; C087 AppSwipeActions; C088 AppPaginationFooter; C090 AppFullScreenModal; C091 AppSnackbarHost.

No new service contract is owned by this unit.


## Ordered checkpoints

| Slice | State | Outcome | Verification |
| --- | --- | --- | --- |
| BDS-09.01 | planned | Explicit asynchronous presentation | V2, V3, V4 |
| BDS-09.02 | planned | Progress and feedback | V2, V3, V4 |
| BDS-09.03 | planned | Menus and anchored presentation | V2, V3, V4 |
| BDS-09.04 | planned | Collection interaction patterns | V2, V3, V4 |
| BDS-09.05 | planned | Adaptive list-detail layout | V2, V3, V4 |
| BDS-09.06 | planned | Presentation hosts | V2, V3, V4 |
| BDS-09.07 | planned | Approved persistence and fixture links | V2, V3 |

Each row is a bounded rolling slice, not a requirement to combine unrelated
component implementations into one commit. Split a row into reviewed sub-checkpoints
when necessary while retaining its obligations and parent identity. Keep only one
implementation slice active across this sequence. Within this RCLD, the next row
depends on the previous row's verified checkpoint. Across RCLDs, the prerequisites
above are the semantic dependency graph; list order alone creates no extra edge.

### BDS-09.01: Explicit asynchronous presentation

Scope: Implement C081–C085 with independent in-flight/retained-content state, retries and sanitized failures.

Definition of green: Cancellation, stale results, initial/empty/offline/error/refresh behavior and duplicate suppression pass.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-09.02: Progress and feedback

Scope: Implement C070–C074 with determinate/indeterminate progress, reduced-motion skeleton and actionable messages.

Definition of green: Accessible busy/progress announcements, action callbacks, expiration and retained state are tested.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-09.03: Menus and anchored presentation

Scope: Implement C061–C065 with focus, bounds and controlled dismissal.

Definition of green: Keyboard/RTL/edge placement, disabled items, outside dismissal and return focus pass.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-09.04: Collection interaction patterns

Scope: Implement C086–C088 with retained content, accessible swipe alternatives and paging suppression.

Definition of green: Refresh/page errors and retry remain deterministic; concurrent/duplicate requests do not corrupt content.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-09.05: Adaptive list-detail layout

Scope: Implement C080 using shared width rules and bounded readable content.

Definition of green: State survives compact/expanded changes, large text and keyboard; pane visibility and back semantics remain correct.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-09.06: Presentation hosts

Scope: Implement C090–C091 using the existing C089 modal ownership and explicit snackbar queue/cancellation.

Definition of green: Modal dismissal, focus/layering, snackbar ordering and cancelled entry cleanup pass.

Verify lane: V2, V3, V4. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

### BDS-09.07: Approved persistence and fixture links

Scope: Implement versioned allowlisted OS recreation and preference behavior, fresh-root launch and safe parser/resolver.

Definition of green: Corrupt/unknown/old payloads recover; duplicate links are handled; no secrets or unfinished forms persist; tab reselect preserves history.

Verify lane: V2, V3. Resolve exact commands from [developer commands](../../development/commands.md) and the actual task graph. New commands must be implemented/documented before being recorded as run.

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

