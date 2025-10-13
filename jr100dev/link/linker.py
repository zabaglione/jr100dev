"""Linker for jr100dev object files."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

from .object_loader import LinkedObject, LinkedSection, LinkedRelocation


class LinkError(RuntimeError):
    pass


@dataclass
class LinkResult:
    origin: int
    entry_point: int
    image: bytes
    symbols: Dict[str, int]


def link_objects(
    objects: Sequence[LinkedObject],
    *,
    entry_override: int | None = None,
    text_base: int | None = None,
    data_base: int | None = None,
    bss_base: int | None = None,
) -> LinkResult:
    if not objects:
        raise LinkError("No objects supplied for linking")

    sections: List[LinkedSection] = []
    for obj in objects:
        sections.extend(obj.sections)

    if not sections:
        raise LinkError("No sections present in objects")

    delta_by_kind: Dict[str, int] = {}
    for kind, base_override in ("code", text_base), ("data", data_base), ("bss", bss_base):
        kind_sections = [s for s in sections if s.kind == kind]
        if not kind_sections:
            delta_by_kind[kind] = 0
            continue
        original_base = min(section.address for section in kind_sections)
        if base_override is None:
            delta_by_kind[kind] = 0
        else:
            delta_by_kind[kind] = base_override - original_base

    adjusted_sections: List[LinkedSection] = [
        LinkedSection(
            name=section.name,
            kind=section.kind,
            address=section.address + delta_by_kind.get(section.kind, 0),
            data=section.data,
            bss_size=section.bss_size,
        )
        for section in sections
    ]

    origin = min(section.address for section in adjusted_sections)
    end_address = max(
        section.address + (len(section.data) if section.data else section.bss_size)
        for section in adjusted_sections
    )
    if end_address - origin > 0x10000:
        raise LinkError("Linked image exceeds 64 KiB address space")

    size = end_address - origin
    image = bytearray(size)
    filled = bytearray(size)

    for section in sorted(adjusted_sections, key=lambda s: s.address):
        offset = section.address - origin
        if section.kind == "bss":
            for index in range(section.bss_size):
                pos = offset + index
                if pos >= size:
                    raise LinkError("Section exceeds allocated image size")
                if not filled[pos]:
                    image[pos] = 0
                    filled[pos] = 1
            continue
        payload = section.data if section.data else [0] * section.bss_size
        for index, value in enumerate(payload):
            pos = offset + index
            if pos >= size:
                raise LinkError("Section exceeds allocated image size")
            if filled[pos]:
                raise LinkError(
                    f"Section overlap detected at address ${section.address + index:04X}"
                )
            image[pos] = value & 0xFF
            filled[pos] = 1

    def _adjust_symbol(value: int) -> int:
        for section in sections:
            length = len(section.data) if section.data else section.bss_size
            if length and section.address <= value < section.address + length:
                return (value + delta_by_kind.get(section.kind, 0)) & 0xFFFF
        return value & 0xFFFF

    symbols: Dict[str, int] = {}
    for obj in objects:
        for name, value in obj.symbols.items():
            adjusted = _adjust_symbol(value)
            if name in symbols and symbols[name] != adjusted:
                raise LinkError(f"Symbol {name} defined with conflicting values")
            symbols[name] = adjusted

    if entry_override is not None:
        entry_point = entry_override & 0xFFFF
    else:
        adjusted_entry_points = {_adjust_symbol(obj.entry_point) for obj in objects}
        if len(adjusted_entry_points) == 1:
            entry_point = adjusted_entry_points.pop() & 0xFFFF
        else:
            entry_point = next(iter(adjusted_entry_points)) & 0xFFFF

    adjusted_map = {section.name: section for section in adjusted_sections}
    _apply_relocations(objects, origin, image, symbols, delta_by_kind)

    return LinkResult(origin=origin & 0xFFFF, entry_point=entry_point, image=bytes(image), symbols=symbols)


def _apply_relocations(
    objects: Sequence[LinkedObject],
    origin: int,
    image: bytearray,
    symbols: Dict[str, int],
    delta_by_kind: Dict[str, int],
) -> None:
    for obj in objects:
        section_map: Dict[str, LinkedSection] = {section.name: section for section in obj.sections}
        for relocation in obj.relocations:
            section = section_map.get(relocation.section)
            if section is None:
                raise LinkError(f"Relocation references unknown section {relocation.section}")
            offset = relocation.offset
            if offset < 0:
                raise LinkError("Relocation offset cannot be negative")
            base_address = section.address + delta_by_kind.get(section.kind, 0)
            absolute = base_address - origin + offset
            if absolute < 0 or absolute + 1 >= len(image):
                raise LinkError("Relocation offset outside of linked image")
            if relocation.target not in symbols:
                raise LinkError(f"Relocation target {relocation.target} is undefined")
            if relocation.type == "relative8":
                value = symbols[relocation.target] & 0xFFFF
            else:
                value = (symbols[relocation.target] + relocation.addend) & 0xFFFF
            if relocation.type == "absolute16":
                image[absolute] = (value >> 8) & 0xFF
                image[absolute + 1] = value & 0xFF
            elif relocation.type == "absolute8":
                image[absolute] = value & 0xFF
            elif relocation.type == "relative8":
                instruction = base_address + relocation.offset - 1
                offset = (value - (instruction + 2)) & 0xFF
                signed = offset if offset < 0x80 else offset - 0x100
                if signed < -128 or signed > 127:
                    raise LinkError(f"Relative relocation out of range for {relocation.target}")
                image[absolute] = offset
            else:
                raise LinkError(f"Unsupported relocation type {relocation.type}")
