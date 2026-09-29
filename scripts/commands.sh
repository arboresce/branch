#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ $# == 1 ]] || {
    echo 'Expected one explicit command' >&2
    exit 2
}
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$PWD/.build/python}"
asset() { uv run --project tools/native-build --locked --no-sync "$@"; }
require_python_environment() {
    if ! uv lock --project tools/native-build --check --offline >/dev/null 2>&1; then
        echo 'The Python tool lockfile is missing or stale.' >&2
        echo 'Run make setup-android or make setup-ios, then retry the check.' >&2
        exit 1
    fi
    if ! uv sync --project tools/native-build --locked --check --offline >/dev/null 2>&1; then
        echo 'The pinned Python tool environment is not prepared or is stale.' >&2
        echo 'Run make setup-android or make setup-ios, then retry the check.' >&2
        exit 1
    fi
}
check_rust() {
    cargo fmt --all --check
    cargo check --workspace --locked
    cargo clippy --workspace --all-targets --locked -- -D warnings
}
check_tools() {
    require_python_environment
    asset branch-native env-check
    asset branch-native config-check
    asset branch-native contract-check
    asset ruff check tools/native-build
    asset ruff format --check tools/native-build
    asset pytest tools/native-build/tests -q -o cache_dir="${BRANCH_BUILD_DIR:-$PWD/.build}/pytest-cache"
    bash -n scripts/commands.sh
}
platform_action() {
    local action="$1" platform="$2"
    case "$action" in
        setup)
            uv sync --project tools/native-build --locked
            asset branch-native setup "$platform"
            ;;
        build | test | dev) asset branch-native "$action" "$platform" ;;
        check)
            check_rust
            check_tools
            asset branch-native check-native "$platform"
            asset branch-native lint "$platform"
            ;;
        verify)
            platform_action check "$platform"
            platform_action test "$platform"
            ;;
    esac
}
case "$1" in
    help) printf '%s\n' 'doctor setup check test verify' 'setup-rust check-rust test-rust verify-rust' 'test-shared' 'setup-ios dev-ios build-ios build-release-ios build-ios-device check-ios test-ios verify-ios' 'setup-android dev-android build-android build-release-android check-android test-android verify-android' ;;
    doctor)
        cargo --version
        rustc --version
        uv --version
        xcodebuild -version
        xcrun swift-format --version
        /usr/libexec/java_home -v 21
        command -v xcodegen
        ;;
    setup-rust) cargo fetch --locked ;;
    check-rust) check_rust ;;
    test-rust) cargo test --workspace --locked ;;
    test-shared) asset branch-native test-shared ;;
    verify-rust)
        check_rust
        cargo test --workspace --locked
        ;;
    check-native-ios) asset branch-native check-native ios ;;
    check-native-android) asset branch-native check-native android ;;
    setup | check | test | verify)
        platform_action "$1" android
        platform_action "$1" ios
        ;;
    build-release-ios) asset branch-native build ios --configuration release ;;
    build-ios-device) asset branch-native build ios --configuration release --sdk device ;;
    build-release-android) asset branch-native build android --configuration release ;;
    setup-ios | dev-ios | build-ios | check-ios | test-ios | verify-ios) platform_action "${1%-ios}" ios ;;
    setup-android | dev-android | build-android | check-android | test-android | verify-android) platform_action "${1%-android}" android ;;
    *)
        echo "Unknown command: $1" >&2
        exit 2
        ;;
esac
