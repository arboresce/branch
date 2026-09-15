import json
import shutil
from pathlib import Path

import pytest
from jsonschema import ValidationError

from branch_native_build import config, native


def fixture(tmp_path):
    shutil.copytree(config.ROOT / "contracts", tmp_path / "contracts")
    for name in ("Cargo.toml", "Cargo.lock"):
        shutil.copyfile(config.ROOT / name, tmp_path / name)
    return tmp_path


def test_settings_are_deterministic_and_versioned(tmp_path):
    root = fixture(tmp_path)
    assert config.settings(root) == (root / "contracts/native-settings.properties").read_bytes()
    path = root / "contracts/application.toml"
    path.write_text(path.read_text().replace('version = "0.1.0"', 'version = "0.2.0"'))
    with pytest.raises(ValueError, match="workspace version"):
        config.contracts(root)


def test_unknown_native_fields_are_rejected(tmp_path):
    root = fixture(tmp_path)
    path = root / "contracts/native-artifacts.toml"
    path.write_text('undeclared = "value"\n' + path.read_text())
    with pytest.raises(ValidationError):
        config.contracts(root)


def cohort(path: Path):
    expected = {"platform": "fixture"}
    (path / "library").write_bytes(b"native fixture")
    (path / "manifest.json").write_text(
        json.dumps({"identity": expected, "outputs": {"library": config.digest(b"native fixture")}})
    )
    return expected


def test_cohort_checks_content_extra_files_and_identity(tmp_path):
    expected = cohort(tmp_path)
    native.verify(tmp_path, expected)
    with pytest.raises(ValueError, match="integrity"):
        native.verify(tmp_path, {"platform": "different"})
    (tmp_path / "extra").write_text("unexpected")
    with pytest.raises(ValueError, match="integrity"):
        native.verify(tmp_path, expected)
    (tmp_path / "extra").unlink()
    (tmp_path / "library").write_bytes(b"edited")
    with pytest.raises(ValueError, match="integrity"):
        native.verify(tmp_path, expected)


def test_cohort_rejects_symlinks(tmp_path):
    expected = cohort(tmp_path)
    (tmp_path / "alias").symlink_to(tmp_path / "library")
    with pytest.raises(ValueError, match="symlink"):
        native.verify(tmp_path, expected)


def test_local_configuration_is_data_not_shell(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "ROOT", tmp_path)
    monkeypatch.delenv("ANDROID_HOME", raising=False)
    (tmp_path / ".env.local").write_text("ANDROID_HOME=$(do-not-execute)\n")
    config.local_environment()
    import os

    assert os.environ["ANDROID_HOME"] == "$(do-not-execute)"
    (tmp_path / ".env.local").write_text("UNSUPPORTED=value\n")
    with pytest.raises(ValueError, match="Invalid local"):
        config.local_environment()
