import json

import pytest

from branch_native_build import config, native


def nested_cohort(path, expected, nested=b"nested metadata"):
    (path / "nested").mkdir()
    (path / "library").write_bytes(b"native fixture")
    (path / "nested/manifest.json").write_bytes(nested)
    outputs = {
        "library": config.digest(b"native fixture"),
        "nested/manifest.json": config.digest(nested),
    }
    (path / "manifest.json").write_text(json.dumps({"identity": expected, "outputs": outputs}))
    return nested


def test_nested_manifest_is_an_ordinary_output(tmp_path):
    expected = {"platform": "fixture"}
    nested = nested_cohort(tmp_path, expected)
    native.verify(tmp_path, expected)
    (tmp_path / "nested/manifest.json").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="integrity"):
        native.verify(tmp_path, expected)
    (tmp_path / "nested/manifest.json").write_bytes(nested)
    (tmp_path / "nested/manifest.json").unlink()
    with pytest.raises(ValueError, match="integrity"):
        native.verify(tmp_path, expected)


def test_nested_unexpected_output_fails(tmp_path):
    expected = {"platform": "fixture"}
    nested_cohort(tmp_path, expected)
    (tmp_path / "nested/extra.json").write_text("unexpected")
    with pytest.raises(ValueError, match="integrity"):
        native.verify(tmp_path, expected)


def test_missing_manifest_fails(tmp_path):
    (tmp_path / "library").write_bytes(b"native fixture")
    with pytest.raises(ValueError, match="manifest is missing"):
        native.verify(tmp_path, {"platform": "fixture"})


def test_incompatible_cohort_schema_fails(tmp_path):
    (tmp_path / "library").write_bytes(b"native fixture")
    manifest = {
        "identity": {"schema_version": 1, "platform": "fixture"},
        "outputs": {"library": config.digest(b"native fixture")},
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="schema is incompatible"):
        native.verify(tmp_path, {"schema_version": 2, "platform": "fixture"})


def test_manifest_byte_change_and_unexpected_root_file_fail(tmp_path):
    expected = {"platform": "fixture"}
    (tmp_path / "library").write_bytes(b"native fixture")
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "identity": expected,
                "outputs": {"library": config.digest(b"native fixture")},
            }
        )
    )
    native.verify(tmp_path, expected)
    (tmp_path / "library").write_bytes(b"edited")
    with pytest.raises(ValueError, match="integrity"):
        native.verify(tmp_path, expected)
    (tmp_path / "library").write_bytes(b"native fixture")
    (tmp_path / "unexpected").write_text("unexpected")
    with pytest.raises(ValueError, match="integrity"):
        native.verify(tmp_path, expected)
