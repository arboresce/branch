import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from .config import ROOT, configure, contracts, digest, output

SCHEMA_VERSION = 2
_OPT_LEVELS = {"0", "1", "2", "3", "s", "z"}
_BUILD_ENV_INPUTS = (
    "RUSTFLAGS",
    "CARGO_ENCODED_RUSTFLAGS",
    "CARGO_BUILD_RUSTFLAGS",
    "RUSTC",
    "RUSTC_WRAPPER",
    "RUSTC_WORKSPACE_WRAPPER",
)
_TARGET_ENV_SUFFIXES = ("LINKER", "RUSTFLAGS")
_PROFILE_ENV_PREFIX = "CARGO_PROFILE_RELEASE_"
_SUPPORTED_PROFILE_ENV = frozenset({"CARGO_PROFILE_RELEASE_OPT_LEVEL"})


def run(*args: str, env: dict | None = None, cwd: Path = ROOT) -> None:
    subprocess.run(args, cwd=cwd, env=env, check=True, stdout=sys.stderr)


def capture(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def _validated_environment() -> dict:
    for key in sorted(os.environ):
        if key.startswith(_PROFILE_ENV_PREFIX) and key not in _SUPPORTED_PROFILE_ENV:
            raise ValueError(f"Unsupported build-affecting override: {key}")
    return dict(os.environ)


def _effective_overrides(platform: str) -> dict:
    environment = _validated_environment()
    overrides = {key: environment[key] for key in _BUILD_ENV_INPUTS if key in environment}
    config = contracts()["native-artifacts"]
    for target in config[platform]["targets"]:
        prefix = f"CARGO_TARGET_{target.upper().replace('-', '_')}_"
        for suffix in _TARGET_ENV_SUFFIXES:
            key = prefix + suffix
            if key in environment:
                overrides[key] = environment[key]
    return overrides


def sdk() -> Path:
    value = os.environ.get("ANDROID_HOME")
    if not value or not Path(value).is_dir():
        raise ValueError("Set ANDROID_HOME to an installed Android SDK")
    return Path(value).resolve()


def identity(platform: str) -> dict:
    config = contracts()
    files = [ROOT / p for p in ("Cargo.toml", "Cargo.lock", "rust-toolchain.toml")]
    for directory in ("core", "app/rust", "contracts", "tools/bindgen"):
        files.extend(
            p
            for p in (ROOT / directory).rglob("*")
            if p.is_file()
            and p.suffix in {".rs", ".toml", ".lock", ".json", ".py"}
            and "__pycache__" not in p.parts
        )
    files.extend(
        ROOT / p
        for p in (
            "tools/native-build/pyproject.toml",
            "tools/native-build/uv.lock",
            "tools/native-build/src/branch_native_build/native.py",
            "tools/native-build/src/branch_native_build/config.py",
        )
    )
    for candidate in (".cargo/config.toml", ".cargo/config"):
        config_file = ROOT / candidate
        if config_file.is_file():
            files.append(config_file)
    if any(p.is_symlink() for p in files):
        raise ValueError("Native sources must not be symlinks")
    inputs = {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in sorted(set(files))}
    toolchain = {
        "rustc": capture("rustc", "-Vv"),
        "opt_level": _release_opt_level(),
        "overrides": _effective_overrides(platform),
    }
    if platform == "ios":
        toolchain["xcode"] = capture("xcodebuild", "-version")
        toolchain["sdk"] = capture("xcrun", "--sdk", "iphoneos", "--show-sdk-version")
        toolchain["deployment_target"] = _deployment_target(
            config["native-artifacts"]["ios"]["minimum_os"]
        )
    else:
        toolchain["ndk"] = (
            sdk() / "ndk" / config["native-artifacts"]["android"]["ndk"] / "source.properties"
        ).read_text()
    return {
        "schema_version": SCHEMA_VERSION,
        "platform": platform,
        "inputs": inputs,
        "toolchain": toolchain,
    }


def _release_opt_level() -> str:
    value = os.environ.get("CARGO_PROFILE_RELEASE_OPT_LEVEL") or "3"
    if value not in _OPT_LEVELS:
        raise ValueError(f"Unsupported CARGO_PROFILE_RELEASE_OPT_LEVEL: {value}")
    return value


def _deployment_target(contract: str) -> str:
    value = os.environ.get("IPHONEOS_DEPLOYMENT_TARGET")
    if not value:
        return contract
    if _version(value) != _version(contract):
        raise ValueError("IPHONEOS_DEPLOYMENT_TARGET conflicts with the native contract")
    return contract


def _version(value: str) -> tuple[int, ...]:
    try:
        parts = [int(part) for part in re.split(r"[.]", value)]
    except ValueError as error:
        raise ValueError(f"Invalid version input: {value}") from error
    return tuple(parts + [0] * (3 - len(parts)))


def location(platform: str, data: dict | None = None) -> Path:
    key = digest(json.dumps(data or identity(platform), sort_keys=True).encode())
    return output() / "native" / platform / key


def verify(path: Path, expected: dict) -> None:
    if path.is_symlink() or not path.is_dir():
        raise ValueError("Native cohort missing or unsafe; run platform build")
    if any(p.is_symlink() for p in path.rglob("*")):
        raise ValueError("Native cohort contains a symlink")
    metadata = path / "manifest.json"
    if not metadata.is_file():
        raise ValueError("Native cohort manifest is missing")
    manifest = json.loads(metadata.read_text())
    if manifest.get("identity", {}).get("schema_version") != expected.get("schema_version"):
        raise ValueError("Native cohort schema is incompatible; rebuild the platform cohort")
    files = [p for p in path.rglob("*") if p.is_file()]
    actual = {str(p.relative_to(path)): digest(p.read_bytes()) for p in files if p != metadata}
    if manifest != {"identity": expected, "outputs": actual} or not actual:
        raise ValueError("Native cohort integrity mismatch")


def check(platform: str) -> Path:
    configure()
    data = identity(platform)
    path = location(platform, data)
    verify(path, data)
    selected = os.environ.get("BRANCH_NATIVE")
    if selected and Path(selected).resolve() != path:
        raise ValueError("Selected native cohort is stale")
    return path


def build(platform: str) -> Path:
    configure()
    data = identity(platform)
    destination = location(platform, data)
    parent = destination.parent
    parent.mkdir(parents=True, exist_ok=True)
    with (parent / ".build.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if destination.exists():
            verify(destination, data)
            return destination
        with tempfile.TemporaryDirectory(prefix=".staging-", dir=parent) as temporary:
            stage = Path(temporary)
            config = contracts()["native-artifacts"]
            target_dir = Path(os.environ.get("CARGO_TARGET_DIR", str(output() / "cargo"))).resolve()
            env = dict(
                _validated_environment(),
                CARGO_TARGET_DIR=str(target_dir),
                BRANCH_BUILD_ID=destination.name,
            )
            for target in config[platform]["targets"]:
                native_env = env.copy()
                if platform == "android":
                    ndk = (
                        sdk()
                        / "ndk"
                        / config["android"]["ndk"]
                        / "toolchains/llvm/prebuilt/darwin-x86_64/bin"
                    )
                    triplet = (
                        "aarch64-linux-android"
                        if target.startswith("aarch64")
                        else "x86_64-linux-android"
                    )
                    compiler = ndk / f"{triplet}{config['android']['minimum_api']}-clang"
                    native_env[f"CARGO_TARGET_{target.upper().replace('-', '_')}_LINKER"] = str(
                        compiler
                    )
                run(
                    "cargo",
                    "build",
                    "--locked",
                    "--release",
                    "-p",
                    "branch-runtime-ffi",
                    "--target",
                    target,
                    env=native_env,
                )
            run("cargo", "build", "--locked", "--release", "-p", "branch-runtime-ffi", env=env)
            bindings = stage / "bindings"
            run(
                "cargo",
                "run",
                "--locked",
                "-p",
                "branch-bindgen",
                "--",
                "generate",
                "--library",
                str(target_dir / "release/libbranch_runtime_ffi.dylib"),
                "--language",
                "swift" if platform == "ios" else "kotlin",
                "--out-dir",
                str(bindings),
                "--no-format",
                env=env,
            )
            if platform == "ios":
                headers = stage / "headers"
                headers.mkdir()
                shutil.copyfile(bindings / "BranchRuntimeFFI.h", headers / "BranchRuntimeFFI.h")
                shutil.copyfile(
                    bindings / "BranchRuntimeFFI.modulemap", headers / "module.modulemap"
                )
                args = ["xcodebuild", "-create-xcframework"]
                for target in config["ios"]["targets"]:
                    args += [
                        "-library",
                        str(target_dir / target / "release/libbranch_runtime_ffi.a"),
                        "-headers",
                        str(headers),
                    ]
                run(*args, "-output", str(stage / "BranchRuntimeFFI.xcframework"))
            else:
                for abi, target in zip(
                    config["android"]["abis"], config["android"]["targets"], strict=True
                ):
                    lib = stage / "jniLibs" / abi / "libbranch_runtime_ffi.so"
                    lib.parent.mkdir(parents=True)
                    shutil.copyfile(target_dir / target / "release/libbranch_runtime_ffi.so", lib)
            if identity(platform) != data:
                raise ValueError("Native inputs changed during build")
            outputs = {
                str(p.relative_to(stage)): digest(p.read_bytes())
                for p in stage.rglob("*")
                if p.is_file()
            }
            (stage / "manifest.json").write_text(
                json.dumps({"identity": data, "outputs": outputs}, indent=2, sort_keys=True) + "\n"
            )
            verify(stage, data)
            stage.rename(destination)
    return destination
