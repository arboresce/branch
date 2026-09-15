# Runtime state contract

Snapshot schema version 1 contains revision, state and runtime objects. Initial
revision is zero. State has preview session_mode and nullable user/workspace context;
no fabricated account is provided. Runtime includes app/core versions, compiled OS,
architecture, target, compiler, profile and build identity. Authentication, network,
persistence and sync remain not_configured.

One native handle owns state. Concurrent reads return identical immutable snapshots.
Shutdown is idempotent and terminal; later reads return Closed. Lock failures and
serialization failures cross FFI as typed errors. No runtime data grants authority.
The screen displays Rust-serialized JSON and does not maintain a Kotlin domain copy.

Application identity is configured in contracts/application.toml: display_name is
branch, store_name is Branch by Arboresce. The runtime identity remains
branch-by-arboresce. Store configuration does not publish a listing.
