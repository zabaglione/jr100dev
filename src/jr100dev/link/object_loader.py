"""Utilities for loading jr100dev object files."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


class ObjectFormatError(RuntimeError):
    pass


@dataclass
class LinkedSection:
    name: str
    kind: str
    address: int
    data: List[int]
    bss_size: int = 0


@dataclass
class LinkedObject:
    source: str
    origin: int
    entry_point: int
    symbols: Dict[str, int]
    sections: List[LinkedSection]
    relocations: List['LinkedRelocation']


@dataclass
class LinkedRelocation:
    section: str
    offset: int
    type: str
    target: str
    addend: int = 0


def load_object(path: Path) -> LinkedObject:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("format") != "jr100dev-object":
        raise ObjectFormatError(f"Unsupported object format in {path}")
    version = payload.get("version")
    if version != 1:
        raise ObjectFormatError(f"Unsupported object version {version} in {path}")

    try:
        origin = int(payload["origin"])
        entry = int(payload["entry_point"])
    except (KeyError, ValueError, TypeError) as exc:
        raise ObjectFormatError(f"Invalid origin or entry point in {path}") from exc

    sections: List[LinkedSection] = []
    for section in payload.get("sections", []):
        name = str(section.get("name", ""))
        kind = str(section.get("kind", "code"))
        address = section.get("address")
        if not isinstance(address, int) or address < 0:
            raise ObjectFormatError(f"Invalid section address in {path}")
        content = section.get("content", "")
        if not isinstance(content, str):
            raise ObjectFormatError(f"Invalid section content in {path}")
        if len(content) % 2 != 0:
            raise ObjectFormatError(f"Section content length must be even in {path}")
        try:
            data = [int(content[i : i + 2], 16) for i in range(0, len(content), 2)]
        except ValueError as exc:
            raise ObjectFormatError(f"Section content is not hex in {path}") from exc
        bss_size = section.get("bss_size", 0)
        if not isinstance(bss_size, int) or bss_size < 0:
            raise ObjectFormatError(f"Invalid bss_size in {path}")
        sections.append(LinkedSection(name=name, kind=kind, address=address, data=data, bss_size=bss_size))

    symbols: Dict[str, int] = {}
    for sym in payload.get("symbols", []):
        name = sym.get("name")
        value = sym.get("value")
        if not isinstance(name, str) or not isinstance(value, int):
            raise ObjectFormatError(f"Invalid symbol entry in {path}")
        symbols[name] = value & 0xFFFF

    entry_point = entry & 0xFFFF

    relocations: List[LinkedRelocation] = []
    for reloc in payload.get("relocations", []):
        section_name = reloc.get("section")
        offset = reloc.get("offset")
        reloc_type = reloc.get("type")
        target = reloc.get("target")
        addend = reloc.get("addend", 0)
        if not all(isinstance(value, str) for value in [section_name, reloc_type, target]):
            raise ObjectFormatError(f"Invalid relocation entry in {path}")
        if not isinstance(offset, int) or offset < 0:
            raise ObjectFormatError(f"Invalid relocation offset in {path}")
        if not isinstance(addend, int):
            raise ObjectFormatError(f"Invalid relocation addend in {path}")
        relocations.append(
            LinkedRelocation(
                section=section_name,
                offset=offset,
                type=reloc_type,
                target=target,
                addend=addend,
            )
        )

    return LinkedObject(
        source=str(payload.get("source", path.name)),
        origin=origin & 0xFFFF,
        entry_point=entry_point,
        symbols=symbols,
        sections=sections,
        relocations=relocations,
    )
