"""Linker for jr100dev object files."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

from .object_loader import LinkedObject, LinkedSection


class LinkError(RuntimeError):
    pass


@dataclass
class LinkResult:
    origin: int
    entry_point: int
    image: bytes
    symbols: Dict[str, int]


def link_objects(objects: Sequence[LinkedObject], *, entry_override: int | None = None) -> LinkResult:
    if not objects:
        raise LinkError("No objects supplied for linking")

    sections: List[LinkedSection] = []
    for obj in objects:
        sections.extend(obj.sections)

    if not sections:
        raise LinkError("No sections present in objects")

    origin = min(section.address for section in sections)
    end_address = max(section.address + len(section.data) for section in sections)
    if end_address - origin > 0x10000:
        raise LinkError("Linked image exceeds 64 KiB address space")

    size = end_address - origin
    image = bytearray(size)
    filled = bytearray(size)

    for section in sorted(sections, key=lambda s: s.address):
        offset = section.address - origin
        for index, value in enumerate(section.data):
            pos = offset + index
            if pos >= size:
                raise LinkError("Section exceeds allocated image size")
            if filled[pos]:
                raise LinkError(
                    f"Section overlap detected at address ${section.address + index:04X}"
                )
            image[pos] = value & 0xFF
            filled[pos] = 1

    symbols: Dict[str, int] = {}
    for obj in objects:
        for name, value in obj.symbols.items():
            if name in symbols and symbols[name] != value:
                raise LinkError(f"Symbol {name} defined with conflicting values")
            symbols[name] = value & 0xFFFF

    entry_points = {obj.entry_point for obj in objects}
    if entry_override is not None:
        entry_point = entry_override & 0xFFFF
    elif len(entry_points) == 1:
        entry_point = entry_points.pop() & 0xFFFF
    else:
        entry_point = objects[0].entry_point & 0xFFFF

    return LinkResult(origin=origin & 0xFFFF, entry_point=entry_point, image=bytes(image), symbols=symbols)
