"""JR-100 `.prg` packer utilities."""
from __future__ import annotations

import struct

_MAGIC = b"PROG"
_SECTION_PNAM = b"PNAM"
_SECTION_PBIN = b"PBIN"
_SECTION_CMNT = b"CMNT"


def pack_prg(
    load_address: int,
    data: bytes,
    entry_point: int,
    *,
    program_name: str = "JR100DEV",
    comment: str = "",
) -> bytes:
    """Create a JR-100 PROG container (version 2) containing one binary section."""

    _validate_bounds(load_address, len(data))

    buffer = bytearray()
    buffer.extend(_MAGIC)
    buffer.extend(struct.pack("<I", 2))  # version

    def write_section(identifier: bytes, payload: bytes) -> None:
        buffer.extend(int.from_bytes(identifier, "little").to_bytes(4, "little"))
        buffer.extend(struct.pack("<I", len(payload)))
        buffer.extend(payload)

    name_bytes = program_name.encode("utf-8")
    write_section(_SECTION_PNAM, struct.pack("<I", len(name_bytes)) + name_bytes)

    entry_comment = f"entry=${entry_point:04X}"
    comment_bytes = entry_comment.encode("utf-8")
    payload = (
        struct.pack("<I", load_address & 0xFFFF)
        + struct.pack("<I", len(data))
        + data
        + struct.pack("<I", len(comment_bytes))
        + comment_bytes
    )
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
