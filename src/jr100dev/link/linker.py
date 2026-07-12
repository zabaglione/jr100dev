"""Linker for jr100dev object files."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from .object_loader import LinkedObject, LinkedSection, LinkedRelocation


class LinkError(RuntimeError):
    pass


@dataclass
class LinkResult:
    origin: int
    entry_point: int
    image: bytes
    symbols: Dict[str, int]
    segments: List['LinkSegment']


@dataclass
class LinkSegment:
    address: int
    data: bytes


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
    for kind, base_override in ("text", text_base), ("data", data_base), ("bss", bss_base):
        kind_sections = [s for s in sections if s.kind == kind]
        if not kind_sections:
            delta_by_kind[kind] = 0
            continue
        original_base = min(section.address for section in kind_sections)
        if base_override is None:
            delta_by_kind[kind] = 0
        else:
            delta_by_kind[kind] = base_override - original_base

    adjusted_sections: List[LinkedSection] = []
    section_address_map: Dict[tuple[int, str], int] = {}
    for obj_index, obj in enumerate(objects):
        for section in obj.sections:
            delta = delta_by_kind.get(section.kind, 0)
            new_address = section.address + delta
            unique_name = f"{section.name}_{obj_index}"
            adjusted_sections.append(
                LinkedSection(
                    name=unique_name,
                    kind=section.kind,
                    address=new_address,
                    data=section.data,
                    bss_size=section.bss_size,
                )
            )
            section_address_map[(obj_index, section.name)] = new_address

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
    used_end = -1

    for section in sorted(adjusted_sections, key=lambda s: s.address):
        length = len(section.data) if section.data else section.bss_size
        if length == 0:
            continue
        offset = section.address - origin
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
        section_end = offset + len(payload)
        if section_end:
            used_end = max(used_end, section_end - 1)

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

    _apply_relocations(objects, origin, image, symbols, section_address_map, delta_by_kind)

    trimmed_image = bytes(image[: used_end + 1]) if used_end >= 0 else bytes()

    merged_segments: List[tuple[int, bytearray]] = []
    for section in sorted(adjusted_sections, key=lambda s: s.address):
        length = len(section.data) if section.data else section.bss_size
        if length == 0:
            continue
        payload = section.data if section.data else [0] * section.bss_size
        data_bytes = bytearray(payload)
        if merged_segments:
            last_address, buffer = merged_segments[-1]
            if last_address + len(buffer) == section.address:
                buffer.extend(data_bytes)
                continue
        merged_segments.append((section.address, data_bytes))

    segments = [LinkSegment(address=addr, data=bytes(buf)) for addr, buf in merged_segments]

    return LinkResult(
        origin=origin & 0xFFFF,
        entry_point=entry_point,
        image=trimmed_image,
        symbols=symbols,
        segments=segments,
    )


def _apply_relocations(
    objects: Sequence[LinkedObject],
    origin: int,
    image: bytearray,
    symbols: Dict[str, int],
    section_address_map: Dict[tuple[int, str], int],
    delta_by_kind: Dict[str, int],
) -> None:
    for obj_index, obj in enumerate(objects):
        sections_by_name = {section.name: section for section in obj.sections}
        for relocation in obj.relocations:
            original_section = sections_by_name.get(relocation.section)
            if original_section is None:
                raise LinkError(f"Relocation references unknown section {relocation.section}")
            adjusted_base = section_address_map[(obj_index, relocation.section)]
            absolute = adjusted_base - origin + (relocation.offset - original_section.address)
            if absolute < 0 or absolute >= len(image):
                raise LinkError("Relocation offset outside of linked image")
            if relocation.target not in symbols:
                raise LinkError(f"Relocation target {relocation.target} is undefined")
            delta_source = delta_by_kind.get(original_section.kind, 0)
            if relocation.type == "relative8":
                difference = symbols[relocation.target] + relocation.addend - delta_source
                if difference < -128 or difference > 127:
                    raise LinkError(f"Relative relocation out of range for {relocation.target}")
                image[absolute] = difference & 0xFF
            elif relocation.type == "absolute16":
                value = (symbols[relocation.target] + relocation.addend) & 0xFFFF
                if absolute + 1 >= len(image):
                    raise LinkError("Relocation write exceeds image size")
                image[absolute] = (value >> 8) & 0xFF
                image[absolute + 1] = value & 0xFF
            elif relocation.type == "absolute8":
                value = (symbols[relocation.target] + relocation.addend) & 0xFFFF
                image[absolute] = value & 0xFF
            else:
                raise LinkError(f"Unsupported relocation type {relocation.type}")
