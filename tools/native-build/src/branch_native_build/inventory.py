import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

from .config import ROOT

_CHECKPOINT = re.compile(r"BDS-[0-9]{2}\.[0-9]{2}")
_REQUIREMENT = re.compile(r"BUI-[0-9]{2}")
_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _declared(text: str, name: str) -> int:
    match = re.search(rf"all\s+([A-Za-z0-9]+)\s+entries\s+in\s+\[the {name} contract", text)
    if not match:
        raise ValueError(f"Missing declared {name} inventory total")
    token = match.group(1)
    if token.isdigit():
        return int(token)
    if token.lower() in _WORDS:
        return _WORDS[token.lower()]
    raise ValueError(f"Unsupported {name} inventory total")


def _schema(root: Path, name: str) -> dict:
    return json.loads((root / "contracts/schemas" / f"{name}.json").read_text())


def _contract(root: Path, name: str) -> dict:
    data = json.loads((root / "contracts" / f"{name}.json").read_text())
    Draft202012Validator(_schema(root, name)).validate(data)
    return data


def _sequence(items: list[dict], prefix: str, label: str, width: int, total: int) -> list[str]:
    identifiers = [item["id"] for item in items]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError(f"Duplicate {label} identifier")
    expected = {f"{prefix}{index:0{width}d}" for index in range(1, total + 1)}
    if set(identifiers) != expected:
        raise ValueError(f"Incomplete {label} inventory")
    return identifiers


def _known(root: Path, pattern: re.Pattern, directory: Path, suffix: str) -> set[str]:
    return {
        match
        for path in sorted(directory.glob(f"*{suffix}"))
        for match in pattern.findall(path.read_text())
    }


def _reference(root: Path, source: Path, value: str) -> None:
    target = (source.parent / value).resolve()
    if not target.is_file() or root.resolve() not in target.parents:
        raise ValueError(f"Broken local reference: {value}")


def validate(root: Path = ROOT) -> dict:
    components = _contract(root, "ui-components")
    services = _contract(root, "platform-services")
    authority = (root / "docs/spec/ui-foundation.md").read_text()
    _sequence(
        components["components"],
        "C",
        "component",
        3,
        _declared(authority, "component"),
    )
    _sequence(
        services["services"],
        "OS",
        "service",
        2,
        _declared(authority, "service"),
    )
    checkpoints = _known(root, _CHECKPOINT, root / "docs/execution/ui-foundation", ".md")
    requirements = _known(root, _REQUIREMENT, root / "docs/spec", "ui-foundation.md")
    if not checkpoints or not requirements:
        raise ValueError("Missing planning authority for inventory references")
    for name, data, key in (
        ("ui-components", components, "components"),
        ("platform-services", services, "services"),
    ):
        source = root / "contracts" / f"{name}.json"
        _reference(root, source, data["authority"])
        for item in data[key]:
            if item["owner_slice"] not in checkpoints:
                raise ValueError(f"Unknown owning slice for {item['id']}: {item['owner_slice']}")
            for requirement in item["requirements"]:
                if requirement not in requirements:
                    raise ValueError(f"Unknown requirement for {item['id']}: {requirement}")
    return {
        "components": len(components["components"]),
        "services": len(services["services"]),
        "checkpoints": len(checkpoints),
        "requirements": len(requirements),
    }
