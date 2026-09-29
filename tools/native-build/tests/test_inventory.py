import json
import shutil

import pytest
from jsonschema import ValidationError

from branch_native_build import config, inventory


def fixture(tmp_path):
    (tmp_path / "contracts/schemas").mkdir(parents=True)
    (tmp_path / "docs/execution/ui-foundation").mkdir(parents=True)
    (tmp_path / "docs/spec").mkdir(parents=True)
    for name in ("ui-components.json", "platform-services.json"):
        shutil.copyfile(config.ROOT / "contracts" / name, tmp_path / "contracts" / name)
        shutil.copyfile(
            config.ROOT / "contracts/schemas" / name, tmp_path / "contracts/schemas" / name
        )
    shutil.copyfile(
        config.ROOT / "docs/spec/ui-foundation.md", tmp_path / "docs/spec/ui-foundation.md"
    )
    for path in (config.ROOT / "docs/execution/ui-foundation").glob("*.md"):
        shutil.copyfile(path, tmp_path / "docs/execution/ui-foundation" / path.name)
    return tmp_path


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
