import pytest

from branch_native_build import environment

_LOCK = """\
version = 1

[[package]]
name = "branch-native-build"
version = "0.1.0"
source = { editable = "." }
dependencies = [
    { name = "jsonschema" },
]

[package.dev-dependencies]
dev = [
    { name = "pytest" },
    { name = "ruff" },
]

[package.metadata]
requires-dist = [{ name = "jsonschema", specifier = "==4.26.0" }]

[package.metadata.requires-dev]
dev = [
    { name = "pytest", specifier = "==9.1.1" },
    { name = "ruff", specifier = "==0.16.6" },
]

[[package]]
name = "attrs"
version = "26.1.0"
"""


def lock_file(tmp_path):
    path = tmp_path / "uv.lock"
    path.write_text(_LOCK)
    return path


def test_synchronized_environment_passes(tmp_path):
    path = lock_file(tmp_path)
    before = path.read_bytes()
    problems = environment.environment_problems(
        path, {"jsonschema": "4.26.0", "pytest": "9.1.1", "ruff": "0.16.6"}
    )
    assert problems == []
    assert path.read_bytes() == before


def test_missing_distributions_fail(tmp_path):
    problems = environment.environment_problems(lock_file(tmp_path), {})
    assert problems == [
        "missing distribution: jsonschema==4.26.0",
        "missing distribution: pytest==9.1.1",
        "missing distribution: ruff==0.16.6",
    ]


def test_stale_distribution_fails(tmp_path):
    problems = environment.environment_problems(
        lock_file(tmp_path), {"jsonschema": "4.25.0", "pytest": "9.1.1", "ruff": "0.16.6"}
    )
    assert problems == ["stale distribution: jsonschema expected 4.26.0 but found 4.25.0"]


def test_required_versions_ignore_transitive_only_packages(tmp_path):
    assert "attrs" not in environment.required_versions(lock_file(tmp_path))


def test_installed_names_are_normalized():
    assert environment._normalize("json_schema") == "json-schema"
    assert environment._normalize("Ruff") == "ruff"


def test_empty_lock_is_rejected(tmp_path):
    path = tmp_path / "uv.lock"
    path.write_text("version = 1\n")
    with pytest.raises(ValueError, match="declares no packages"):
        environment.locked_versions(path)
