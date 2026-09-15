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
system appearance, loading and error states. There are no tabs or navigation flows.
