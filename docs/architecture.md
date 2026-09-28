# Architecture

The current hosts target iOS and Android. Desktop support remains outside this
mobile bootstrap.

branch-domain owns the serializable application domain. branch-runtime owns
one in-memory state handle and diagnostic serialization. branch-runtime-ffi exports
that runtime through UniFFI; no platform owns a second domain model.

The mobile design uses one shared Compose diagnostic screen. Android calls generated
Kotlin bindings; iOS calls generated Swift bindings and supplies snapshot text to the
Compose view controller. Bindings are platform-specific; JVM bindings are not used
in Kotlin/Native. Native hosts manage lifecycle and off-main-thread calls.

The initial view is a scrollable, selectable JSON document with safe-area padding,
system appearance, loading and error states. The current bootstrap has no tabs or
navigation flows; the UI Foundation v1 target adds a shared navigation owner and
additional presentation modules as described below.

## UI foundation ownership

The [UI Foundation v1](spec/ui-foundation.md) target adds shared presentation
modules without changing Rust authority. Module responsibilities are:

- `app/ui/design-system` owns typed theme, resources, controls, semantics and the
  internal glass renderer.
- `app/ui/patterns` owns scaffolds and async, collection and modal patterns.
- `app/platform` owns service contracts and lifecycle-safe Android/iOS implementations.
- `app/shared/app` owns the common application root, presentation assembly and navigation.
- `app/shared/xc-framework` exposes the minimal Swift-facing controller bridge.
- `app/catalog` is a development consumer excluded from production dependencies.
- `app/ui/diagnostic/public` and the existing hosts remain real runtime consumers.

Every C001-C092 export in `contracts/ui-components.json` is assigned to
`:ui:design-system` or `:ui:patterns` and to one owning BDS slice, and every
OS01-OS10 entry in `contracts/platform-services.json` is assigned to a BDS slice
and the `:platform` implementations. `branch-native contract-check` validates the
unique identifiers, complete inventories, owning slices, requirements and local
references. Component implementation status remains owned by the BDS execution
ledger, not by the inventory.

Exclusions and approved persistence remain as the specification states: no
Desktop/web target, backend, account, payment, analytics, remote flag, store
distribution or external publication, and no second domain model. Theme/effects
preferences, allowlisted navigation restoration and the no-secret-on-disk rule are
owned by BDS-09.
