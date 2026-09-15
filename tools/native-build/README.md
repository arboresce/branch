# Native build tooling

This Python package validates the repository's contracts and produces immutable
Rust binding/library cohorts. It uses pinned dependencies in uv.lock and emits
artifacts under BRANCH_BUILD_DIR or the repository's ignored .build directory.

Internal producer entry points, from the Branch project directory:

```sh
uv sync --project tools/native-build --locked
uv run --project tools/native-build --locked --no-sync branch-native config-write
uv run --project tools/native-build --locked --no-sync branch-native config-check
uv run --project tools/native-build --locked --no-sync branch-native build-native android
uv run --project tools/native-build --locked --no-sync branch-native build-native ios
uv run --project tools/native-build --locked --no-sync branch-native check-native android
uv run --project tools/native-build --locked --no-sync branch-native check-native ios
```

Native Rust targets and SDKs must already be installed for these internal commands.
The mobile Make commands compose tool setup, production and app builds for normal
development through the explicit platform targets.

A cohort manifest records input/toolchain identity and every output hash. Source
changes during a build, modified outputs, unexpected files, stale selected cohorts
and symlinked output contents fail checks. Hashes provide local integrity, not a
signature or independent proof of reproducibility. Reuse only complete verified
cohorts; existing corrupt artifacts are not overwritten automatically.

Run the package tests with
`uv run --project tools/native-build --locked --no-sync pytest tools/native-build/tests`. Contract schemas are closed and compare UniFFI/app
versions to their Cargo authorities. No local environment file is evaluated as shell.
