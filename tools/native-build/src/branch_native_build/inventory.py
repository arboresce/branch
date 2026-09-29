import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

from .config import ROOT

_CHECKPOINT = re.compile(r"BDS-[0-9]{2}\.[0-9]{2}")
_CHECKPOINT_SECTION = re.compile(r"^#{2,3}\s+(BDS-[0-9]{2}\.[0-9]{2}):\s*(.*)$", re.MULTILINE)
_REQUIREMENT_SECTION = re.compile(r"^##\s+(BUI-[0-9]{2}):\s*(.*)$", re.MULTILINE)
_NEXT_HEADING = re.compile(r"\n#{2,3}\s")
_MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_MARKDOWN_HEADING = re.compile(r"^#{1,6}\s+(.*)$", re.MULTILINE)
_VERIFY_LANE = re.compile(r"Verify lane:\s*([^\n]+)")
_VERIFICATION_LANES = frozenset({"V0", "V1", "V2", "V3", "V4", "V5", "V6"})
_PLAN_DIRECTORY = "docs/execution/ui-foundation"
_SPEC = "docs/spec/ui-foundation.md"
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


def _section_body(text: str, end: int) -> str:
    remainder = text[end:]
    following = _NEXT_HEADING.search(remainder)
    return remainder if following is None else remainder[: following.start()]


def _verification_lanes(value: str, identifier: str) -> tuple[str, ...]:
    head = value.split(".", 1)[0]
    lanes = tuple(re.findall(r"V[0-9]+", head))
    if not lanes:
        raise ValueError(f"Missing verification lane: {identifier}")
    unknown = sorted({lane for lane in lanes if lane not in _VERIFICATION_LANES})
    if unknown:
        raise ValueError(f"Unknown verification lane {unknown[0]}: {identifier}")
    return lanes


def _clause(body: str, label: str) -> str | None:
    pattern = rf"{re.escape(label)}:(.*?)(?=\n(?:Scope:|Definition of green:|Verify lane:)|\Z)"
    match = re.search(pattern, body, re.DOTALL)
    return None if match is None else match.group(1)


def _checkpoint_definitions(root: Path) -> set[str]:
    directory = root / _PLAN_DIRECTORY
    tables: dict[str, Path] = {}
    sections: dict[str, Path] = {}
    for path in sorted(directory.glob("*.md")):
        text = path.read_text()
        for line in text.splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if not cells or not _CHECKPOINT.fullmatch(cells[0]):
                continue
            identifier = cells[0]
            if len(cells) < 4 or not cells[2] or not cells[3]:
                raise ValueError(f"Incomplete checkpoint table row: {identifier}")
            _verification_lanes(cells[3], identifier)
            if identifier in tables:
                raise ValueError(f"Duplicate checkpoint definition: {identifier}")
            tables[identifier] = path
        for match in _CHECKPOINT_SECTION.finditer(text):
            identifier = match.group(1)
            if not match.group(2).strip():
                raise ValueError(f"Missing checkpoint section title: {identifier}")
            if identifier in sections:
                raise ValueError(f"Duplicate checkpoint definition: {identifier}")
            body = _section_body(text, match.end())
            scope = _clause(body, "Scope")
            green = _clause(body, "Definition of green")
            if not scope or not scope.strip() or not green or not green.strip():
                raise ValueError(f"Incomplete checkpoint section definition: {identifier}")
            lane = _VERIFY_LANE.search(body)
            if not lane:
                raise ValueError(f"Missing verification lane: {identifier}")
            _verification_lanes(lane.group(1), identifier)
            sections[identifier] = path
    if not tables:
        raise ValueError("Missing planning authority for inventory references")
    for identifier, table_path in tables.items():
        section_path = sections.get(identifier)
        if section_path is None:
            raise ValueError(f"Checkpoint table row lacks a matching section: {identifier}")
        if section_path != table_path:
            raise ValueError(f"Checkpoint table and section are not in the same plan: {identifier}")
    section_only = sorted(set(sections) - set(tables))
    if section_only:
        raise ValueError(f"Checkpoint section lacks a matching table row: {section_only[0]}")
    return set(tables)


def _requirement_definitions(root: Path) -> set[str]:
    text = (root / _SPEC).read_text()
    definitions = set()
    for match in _REQUIREMENT_SECTION.finditer(text):
        identifier = match.group(1)
        if not match.group(2).strip():
            raise ValueError(f"Missing requirement section title: {identifier}")
        if identifier in definitions:
            raise ValueError(f"Duplicate requirement definition: {identifier}")
        definitions.add(identifier)
    if not definitions:
        raise ValueError("Missing planning authority for inventory references")
    return definitions


def _reference(root: Path, source: Path, value: str) -> None:
    target = (source.parent / value).resolve()
    if not target.is_file() or root.resolve() not in target.parents:
        raise ValueError(f"Broken local reference: {value}")


def _slug(heading: str) -> str:
    without_punctuation = re.sub(r"[^\w\s-]", "", heading.strip().lower())
    return re.sub(r"\s+", "-", without_punctuation).strip("-")


def _anchors(text: str) -> set[str]:
    return {_slug(match.group(1)) for match in _MARKDOWN_HEADING.finditer(text)}


def _validate_links(root: Path, source: Path) -> None:
    root_resolved = root.resolve()
    for match in _MARKDOWN_LINK.finditer(source.read_text()):
        raw = match.group(1)
        if raw.startswith(("http://", "https://", "mailto:")):
            continue
        path_part, _, anchor = raw.partition("#")
        if path_part:
            target = (source.parent / path_part).resolve()
            if not target.is_file() or root_resolved not in target.parents:
                raise ValueError(f"Broken local reference: {raw}")
        else:
            target = source
        if anchor and anchor not in _anchors(target.read_text()):
            raise ValueError(f"Broken local anchor: {raw}")


def validate(root: Path = ROOT) -> dict:
    components = _contract(root, "ui-components")
    services = _contract(root, "platform-services")
    authority = (root / _SPEC).read_text()
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
    checkpoints = _checkpoint_definitions(root)
    requirements = _requirement_definitions(root)
    _validate_links(root, root / _SPEC)
    for path in sorted((root / _PLAN_DIRECTORY).glob("*.md")):
        _validate_links(root, path)
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
