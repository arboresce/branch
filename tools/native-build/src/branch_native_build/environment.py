import importlib.metadata
import tomllib
from pathlib import Path


def _normalize(name: str) -> str:
    return name.lower().replace("_", "-").replace(".", "-")


def _pinned_version(entry: dict) -> str | None:
    specifier = entry.get("specifier")
    if isinstance(specifier, str) and specifier.startswith("=="):
        return specifier.removeprefix("==")
    return None


def locked_versions(lock: Path) -> dict[str, str]:
    data = tomllib.loads(lock.read_text())
    versions: dict[str, str] = {}
    for package in data.get("package", []):
        name, version = package.get("name"), package.get("version")
        if name and version:
            versions[_normalize(name)] = version
    if not versions:
        raise ValueError("The Python lockfile declares no packages")
    return versions


def required_versions(lock: Path) -> dict[str, str]:
    data = tomllib.loads(lock.read_text())
    required: dict[str, str] = {}
    for package in data.get("package", []):
        if "editable" not in package.get("source", {}):
            continue
        metadata = package.get("metadata", {})
        entries = list(metadata.get("requires-dist", []))
        for group in metadata.get("requires-dev", {}).values():
            entries.extend(group)
        for entry in entries:
            version = _pinned_version(entry)
            if version is not None:
                required[_normalize(entry["name"])] = version
    if not required:
        raise ValueError("The Python lockfile declares no direct dependencies")
    return required


def installed_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata["Name"]
        if name:
            versions[_normalize(name)] = distribution.version
    return versions


def environment_problems(lock: Path, installed: dict[str, str]) -> list[str]:
    problems: list[str] = []
    for name, expected in sorted(required_versions(lock).items()):
        actual = installed.get(name)
        if actual is None:
            problems.append(f"missing distribution: {name}=={expected}")
        elif actual != expected:
            problems.append(f"stale distribution: {name} expected {expected} but found {actual}")
    return problems
