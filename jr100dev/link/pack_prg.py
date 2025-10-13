"""JR-100 `.prg` packer utilities."""
from __future__ import annotations

import struct
from typing import Iterable, Sequence, Tuple

_MAGIC = b"PROG"
_SECTION_PNAM = b"PNAM"
_SECTION_PBIN = b"PBIN"
_SECTION_CMNT = b"CMNT"


Segment = Tuple[int, bytes]


def pack_prg(
    load_address: int,
    data: bytes | None,
    entry_point: int,
    *,
    segments: Sequence[Segment] | None = None,
    program_name: str = "JR100DEV",
    comment: str = "",
) -> bytes:
    """Create a JR-100 PROG container (version 2).

    `segments` が指定された場合は各セグメントを個別の PBIN セクションとして格納する。
    未指定時は `load_address` と `data` を 1 セクションとして利用する。
    """

    if segments is None:
        if data is None:
            raise ValueError("Either data or segments must be supplied")
        segments_to_use: Sequence[Segment] = [(load_address, data)]
    else:
        if not segments:
            raise ValueError("segments must not be empty")
        segments_to_use = sorted(segments, key=lambda item: item[0])

    buffer = bytearray()
    buffer.extend(_MAGIC)
    buffer.extend(struct.pack("<I", 2))  # version

    def write_section(identifier: bytes, payload: bytes) -> None:
        buffer.extend(int.from_bytes(identifier, "little").to_bytes(4, "little"))
        buffer.extend(struct.pack("<I", len(payload)))
        buffer.extend(payload)

    name_bytes = program_name.encode("utf-8")
    write_section(_SECTION_PNAM, struct.pack("<I", len(name_bytes)) + name_bytes)

    entry_comment = f"entry=${entry_point:04X}".encode("utf-8")

    seen_ranges: list[tuple[int, int]] = []
    for index, (segment_address, segment_data) in enumerate(segments_to_use):
        _validate_bounds(segment_address, len(segment_data))
        _guard_overlap(seen_ranges, segment_address, len(segment_data))
        seen_ranges.append((segment_address, segment_address + len(segment_data)))
        payload = (
            struct.pack("<I", segment_address & 0xFFFF)
            + struct.pack("<I", len(segment_data))
            + segment_data
        )
        if index == 0:
            payload += struct.pack("<I", len(entry_comment)) + entry_comment
        else:
            payload += struct.pack("<I", 0)
        write_section(_SECTION_PBIN, payload)

    if comment:
        user_comment = comment.encode("utf-8")
        write_section(_SECTION_CMNT, struct.pack("<I", len(user_comment)) + user_comment)

    return bytes(buffer)


def _validate_bounds(load_address: int, length: int) -> None:
    if load_address < 0 or load_address > 0xFFFF:
        raise ValueError(f"load address out of range: {load_address}")
    if length < 0 or length > 0x10000:
        raise ValueError(f"payload too large: {length}")
    if load_address + length > 0x10000:
        raise ValueError("payload extends beyond 64 KiB address space")


def _guard_overlap(ranges: Iterable[tuple[int, int]], start: int, length: int) -> None:
    end = start + length
    for existing_start, existing_end in ranges:
        if not (end <= existing_start or start >= existing_end):
            raise ValueError("segment ranges overlap")
