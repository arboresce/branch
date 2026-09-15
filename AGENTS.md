# Repository guidance

This project owns branch-by-arboresce, its mobile hosts, presentation, Rust core and native bindings.
Read the [instruction index](docs/agents/README.md) and nearest applicable instructions.

Keep each change coherent and verified. Preserve unrelated work. Do not copy credentials,
personal information or another checkout's configuration into source or documentation.
Use project-local links and dependencies. A normal checkout must support documented
builds using this project and documented public tools alone. Keep Rust application
state authoritative; platform code owns presentation, lifecycle and OS integration.

Use exact documented Make targets. Make routes to scripts/commands.sh. Developer
commands are explicit: no caller TARGET selectors. Use dev for interactive apps;
reserve up/down for background services if any are added. Check must not repair drift.
Keep lockfiles and wrapper checksums committed. Generated native build artifacts are
not source; bindings and libraries must belong to the same verified build cohort.

Keep documentation accurate in each implementation change. State proposed and verified
behavior separately. Retain rights and attribution; source licensing does not grant
brand rights. Use only approved material. Review staged contents and commit metadata.
Run make verify-rust for Rust changes and platform verification for native changes.
Report checks actually run, skipped checks and remaining risks. Commits and external
publication require applicable user authorization.

Handwritten source contains no explanatory comments or docstrings; keep rationale in
existing documentation. Preserve required interpreter directives, legal notices and
upstream/generated files. Rust package names follow branch-<directory-role>: domain
is branch-domain, runtime is branch-runtime, and runtime-ffi is branch-runtime-ffi.
Rust underscore import/library names must match those package identities. Kotlin
package declarations must match their source directories.
