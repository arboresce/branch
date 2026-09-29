import json
import re
import shutil

import pytest
from jsonschema import ValidationError

from branch_native_build import config, inventory


def fixture(tmp_path):
    (tmp_path / "contracts/schemas").mkdir(parents=True)
    for name in ("ui-components.json", "platform-services.json"):
        shutil.copyfile(config.ROOT / "contracts" / name, tmp_path / "contracts" / name)
        shutil.copyfile(
            config.ROOT / "contracts/schemas" / name, tmp_path / "contracts/schemas" / name
        )
    shutil.copytree(config.ROOT / "docs/spec", tmp_path / "docs/spec")
    shutil.copytree(config.ROOT / "docs/development", tmp_path / "docs/development")
    (tmp_path / "docs/execution/ui-foundation").mkdir(parents=True)
    for path in (config.ROOT / "docs/execution/ui-foundation").glob("*.md"):
        shutil.copyfile(path, tmp_path / "docs/execution/ui-foundation" / path.name)
    return tmp_path


def plan(root, name):
    return root / "docs/execution/ui-foundation" / name


def section_text(text, identifier):
    match = re.search(
        rf"^### {re.escape(identifier)}:.*?(?=\n### |\Z)", text, re.MULTILINE | re.DOTALL
    )
    assert match is not None, identifier
    return match.group(0)


def load(root, name):
    return json.loads((root / "contracts" / f"{name}.json").read_text())


def save(root, name, data):
    (root / "contracts" / f"{name}.json").write_text(json.dumps(data))


def checkpoint_row(root, identifier):
    plan = root / "docs/execution/ui-foundation/bds-00-contracts.md"
    for line in plan.read_text().splitlines():
        if line.startswith(f"| {identifier} "):
            return plan, line + "\n"
    raise AssertionError(f"Missing checkpoint row: {identifier}")


def test_valid_inventory_passes(tmp_path):
    summary = inventory.validate(fixture(tmp_path))
    assert summary == {"components": 92, "services": 10, "checkpoints": 65, "requirements": 12}


def test_duplicate_component_identifier_fails(tmp_path):
    root = fixture(tmp_path)
    data = load(root, "ui-components")
    data["components"][1]["id"] = data["components"][0]["id"]
    save(root, "ui-components", data)
    with pytest.raises(ValueError, match="Duplicate component"):
        inventory.validate(root)


def test_incomplete_component_inventory_fails(tmp_path):
    root = fixture(tmp_path)
    data = load(root, "ui-components")
    data["components"].pop()
    save(root, "ui-components", data)
    with pytest.raises(ValueError, match="Incomplete component"):
        inventory.validate(root)


def test_unknown_owning_slice_fails(tmp_path):
    root = fixture(tmp_path)
    data = load(root, "ui-components")
    data["components"][0]["owner_slice"] = "BDS-99.99"
    save(root, "ui-components", data)
    with pytest.raises(ValueError, match="Unknown owning slice"):
        inventory.validate(root)


def test_unknown_requirement_fails(tmp_path):
    root = fixture(tmp_path)
    data = load(root, "platform-services")
    data["services"][0]["requirements"] = ["BUI-99"]
    save(root, "platform-services", data)
    with pytest.raises(ValueError, match="Unknown requirement"):
        inventory.validate(root)


def test_undeclared_field_fails(tmp_path):
    root = fixture(tmp_path)
    data = load(root, "ui-components")
    data["components"][0]["undeclared"] = "value"
    save(root, "ui-components", data)
    with pytest.raises(ValidationError):
        inventory.validate(root)


def test_broken_authority_reference_fails(tmp_path):
    root = fixture(tmp_path)
    data = load(root, "platform-services")
    data["authority"] = "../docs/spec/missing.md"
    save(root, "platform-services", data)
    with pytest.raises(ValueError, match="Broken local reference"):
        inventory.validate(root)


def test_orphan_mention_is_not_a_checkpoint_definition(tmp_path):
    root = fixture(tmp_path)
    plan = root / "docs/execution/ui-foundation/bds-00-contracts.md"
    plan.write_text(plan.read_text() + "\nProse mention of BDS-99.99 is not a definition.\n")
    summary = inventory.validate(root)
    assert summary["checkpoints"] == 65
    data = load(root, "ui-components")
    data["components"][0]["owner_slice"] = "BDS-99.99"
    save(root, "ui-components", data)
    with pytest.raises(ValueError, match="Unknown owning slice"):
        inventory.validate(root)


def test_duplicate_checkpoint_definition_fails(tmp_path):
    root = fixture(tmp_path)
    plan, row = checkpoint_row(root, "BDS-00.02")
    plan.write_text(plan.read_text().replace(row, row + row))
    with pytest.raises(ValueError, match="Duplicate checkpoint definition"):
        inventory.validate(root)


def test_checkpoint_table_row_without_section_fails(tmp_path):
    root = fixture(tmp_path)
    plan, row = checkpoint_row(root, "BDS-00.02")
    plan.write_text(
        plan.read_text().replace(row, row + "| BDS-00.09 | planned | Orphan row | V0 |\n")
    )
    with pytest.raises(ValueError, match="lacks a matching section"):
        inventory.validate(root)


def test_checkpoint_section_without_table_row_fails(tmp_path):
    root = fixture(tmp_path)
    plan, row = checkpoint_row(root, "BDS-00.02")
    plan.write_text(plan.read_text().replace(row, ""))
    with pytest.raises(ValueError, match="lacks a matching table row"):
        inventory.validate(root)


def test_duplicate_requirement_definition_fails(tmp_path):
    root = fixture(tmp_path)
    spec = root / "docs/spec/ui-foundation.md"
    spec.write_text(spec.read_text() + "\n## BUI-01: Duplicate definition\n\nbody\n")
    with pytest.raises(ValueError, match="Duplicate requirement definition"):
        inventory.validate(root)


def test_checkpoint_section_moved_to_another_plan_fails(tmp_path):
    root = fixture(tmp_path)
    source = plan(root, "bds-00-contracts.md")
    target = plan(root, "bds-01-native-build.md")
    text = source.read_text()
    moved = section_text(text, "BDS-00.02")
    source.write_text(text.replace(moved, ""))
    target.write_text(target.read_text() + "\n" + moved)
    with pytest.raises(ValueError, match="not in the same plan"):
        inventory.validate(root)


def test_removed_verification_lane_fails(tmp_path):
    root = fixture(tmp_path)
    path = plan(root, "bds-00-contracts.md")
    path.write_text(path.read_text().replace("Verify lane: V0, V1. Resolve", "Resolve", 1))
    with pytest.raises(ValueError, match="verification lane"):
        inventory.validate(root)


def test_unknown_verification_lane_fails(tmp_path):
    root = fixture(tmp_path)
    path = plan(root, "bds-00-contracts.md")
    path.write_text(
        path.read_text().replace("Verify lane: V0, V1. Resolve", "Verify lane: V9. Resolve", 1)
    )
    with pytest.raises(ValueError, match="Unknown verification lane"):
        inventory.validate(root)


def test_empty_scope_definition_fails(tmp_path):
    root = fixture(tmp_path)
    path = plan(root, "bds-00-contracts.md")
    text = path.read_text()
    section = section_text(text, "BDS-00.02")
    stripped = re.sub(r"Scope:[^\n]*\n", "Scope:\n", section)
    path.write_text(text.replace(section, stripped))
    with pytest.raises(ValueError, match="Incomplete checkpoint section definition"):
        inventory.validate(root)


def test_broken_plan_to_spec_link_fails(tmp_path):
    root = fixture(tmp_path)
    path = plan(root, "bds-00-contracts.md")
    path.write_text(
        path.read_text().replace("../../spec/ui-foundation.md)", "../../spec/missing.md)", 1)
    )
    with pytest.raises(ValueError, match="Broken local reference"):
        inventory.validate(root)


def test_broken_spec_anchor_fails(tmp_path):
    root = fixture(tmp_path)
    path = plan(root, "bds-00-contracts.md")
    path.write_text(
        path.read_text().replace(
            "ui-foundation.md#bui-11-verification-and-completion)",
            "ui-foundation.md#missing-anchor)",
            1,
        )
    )
    with pytest.raises(ValueError, match="Broken local anchor"):
        inventory.validate(root)
