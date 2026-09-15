import hashlib
import json
import os
import tomllib
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[4]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def contracts(root: Path = ROOT) -> dict:
    result = {}
    for name in ("application", "native-artifacts", "development"):
        path = root / "contracts" / f"{name}.toml"
        schema = json.loads((root / "contracts/schemas" / f"{name}.json").read_text())
        data = tomllib.loads(path.read_text())
        Draft202012Validator(schema).validate(data)
        result[name] = data
    app = result["application"]
    workspace = tomllib.loads((root / "Cargo.toml").read_text())
    if workspace["workspace"]["package"]["version"] != app["version"]:
        raise ValueError("Application and workspace version differ")
    packages = tomllib.loads((root / "Cargo.lock").read_text())["package"]
    versions = {p["version"] for p in packages if p["name"] == "uniffi"}
    if versions != {result["native-artifacts"]["uniffi_version"]}:
        raise ValueError("UniFFI contract differs from Cargo.lock")
    return result


def output() -> Path:
    return Path(os.environ.get("BRANCH_BUILD_DIR", str(ROOT / ".build"))).resolve()


def settings(root: Path = ROOT) -> bytes:
    data = contracts(root)
    app, android = data["application"], data["native-artifacts"]["android"]
    fields = {
        "applicationId": app["bundle_id"],
        "displayName": app["display_name"],
        "versionName": app["version"],
        "versionCode": app["version_code"],
        "compileSdk": android["compile_sdk"],
        "minSdk": android["minimum_api"],
        "targetSdk": android["target_sdk"],
        "ndkVersion": android["ndk"],
        "abis": ",".join(android["abis"]),
    }
    return (
        "# Generated from application/native contracts; do not edit.\n"
        + "".join(f"{k}={v}\n" for k, v in sorted(fields.items()))
    ).encode()


def configure(write: bool = False) -> None:
    path = ROOT / "contracts/native-settings.properties"
    expected = settings()
    if write:
        path.write_bytes(expected)
    elif not path.exists() or path.read_bytes() != expected:
        raise ValueError("Native settings drift; run the platform setup command")


def local_environment() -> None:
    path = ROOT / ".env.local"
    allowed = {
        "IOS_SIMULATOR_ID",
        "ANDROID_SERIAL",
        "ANDROID_HOME",
        "JAVA_HOME",
        "BRANCH_BUILD_DIR",
    }
    if path.exists():
        for line in path.read_text().splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            key, sep, value = line.partition("=")
            if not sep or key not in allowed or not value or any(c in value for c in "\n\r\0"):
                raise ValueError("Invalid local configuration entry")
            os.environ.setdefault(key, value)
