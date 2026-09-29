#!/usr/bin/env bash
set -euo pipefail

app="${TARGET_BUILD_DIR:-}/${WRAPPER_NAME:-}"
source="${BRANCH_COMPOSE_RESOURCES:-}"
destination="${BRANCH_COMPOSE_BUNDLE:-}"
expected="${app}/compose-resources/composeResources"

if [ -z "${TARGET_BUILD_DIR:-}" ] || [ -z "${WRAPPER_NAME:-}" ] || [ -z "$source" ] || [ -z "$destination" ]; then
    echo "Compose resource installation requires an app product and resource paths" >&2
    exit 1
fi
if [ "$destination" != "$expected" ]; then
    echo "Refusing unbounded Compose resource destination" >&2
    exit 1
fi
if [ -L "$app" ]; then
    echo "Refusing symlinked app product" >&2
    exit 1
fi
app_real="$(cd "$app" && pwd -P)"
for component in "$app/compose-resources" "$destination"; do
    if [ -L "$component" ]; then
        echo "Refusing symlinked Compose resource destination" >&2
        exit 1
    fi
done
if [ -d "$app/compose-resources" ]; then
    parent_real="$(cd "$app/compose-resources" && pwd -P)"
    case "$parent_real" in
        "$app_real"/*) ;;
        *)
            echo "Compose resource destination escapes the selected app" >&2
            exit 1
            ;;
    esac
fi
if [ -L "$source" ] || [ ! -d "$source" ]; then
    echo "Missing shared Compose resources" >&2
    exit 1
fi
if [ -n "$(find "$source" -type l -print -quit)" ]; then
    echo "Refusing symlinked Compose resource source" >&2
    exit 1
fi
if [ -z "$(find "$source" -type f -print -quit)" ]; then
    echo "Empty shared Compose resources" >&2
    exit 1
fi
rm -rf "$destination"
mkdir -p "$destination"
cp -R "$source/." "$destination/"
