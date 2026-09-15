# Troubleshooting

- **Tool missing:** run `make doctor`, install the named prerequisite, then use
  the platform setup command. Do not silently substitute compiler versions.
- **Native settings drift:** review contracts, then run platform setup to regenerate
  settings. Check commands intentionally leave source unchanged.
- **Native cohort missing or stale:** run the platform build command. It creates a
  new source-addressed cohort; do not redirect an app to an arbitrary old directory.
- **Native integrity mismatch:** an existing immutable artifact was edited. Preserve
  it for diagnosis and choose a fresh build output directory rather than overwriting it.
- **Dependency verification failure:** inspect the changed dependency before deliberately
  updating locks/checksums. Do not disable verification to get a build through.
- **Simulator unavailable:** install the runtime selected by development.toml, or
  explicitly select an available simulator with IOS_SIMULATOR_ID.
- **Emulator startup failure:** inspect android-emulator.log in the output directory.
  Ensure Android SDK tools are installed and ANDROID_USER_HOME/ANDROID_AVD_HOME, if
  supplied through the environment, point to consistent writable locations.
- **Runtime Closed:** a native handle was shut down. Create a new lifecycle owner;
  retrying a terminal handle is not a recovery policy.
- **Null account context:** this is intentional preview state. Authentication,
  networking, persistence and sync have not been implemented.

Build through the documented Make commands. The generated Xcode project is an
output for inspection, not a separately maintained source of build configuration.
