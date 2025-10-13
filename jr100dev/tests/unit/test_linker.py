import json
import struct
from types import SimpleNamespace

import pytest

from jr100dev.cli.main import run_assemble, run_link
from jr100dev.link.linker import LinkError, link_objects
from jr100dev.link.object_loader import load_object


def _assemble_to_object(tmp_path, name: str, source: str):
    src = tmp_path / f"{name}.asm"
    src.write_text(source)
    obj_path = tmp_path / f"{name}.json"
    args = SimpleNamespace(
        source=src,
        output=tmp_path / f"{name}.prg",
        bin=None,
        obj=obj_path,
        map=None,
        lst=None,
        entry=None,
        name=None,
        comment=None,
    )
    rc = run_assemble(args)
    assert rc == 0
    return obj_path


def test_link_objects_combines_sections(tmp_path):
    obj1_path = _assemble_to_object(
        tmp_path,
        "part1",
        """
        .org $0300
        PART1: LDAA #1
               RTS
        """,
    )
    obj2_path = _assemble_to_object(
        tmp_path,
        "part2",
        """
        .org $0320
        PART2: LDAA #2
               RTS
        """,
    )

    objects = [load_object(obj1_path), load_object(obj2_path)]
    result = link_objects(objects)
    assert result.origin == 0x0300
    assert result.entry_point in (0x0300, 0x0320)
    assert result.symbols["PART1"] == 0x0300
    assert result.symbols["PART2"] == 0x0320
    assert [segment.address for segment in result.segments] == [0x0300, 0x0320]
    offset = 0x0320 - result.origin
    assert result.image[0] == 0x86
    assert result.image[offset] == 0x86


def test_link_overlap_detected(tmp_path):
    obj_path = _assemble_to_object(
        tmp_path,
        "overlap",
        """
        .org $0300
        LABEL: LDAA #1
               RTS
        """,
    )
    data = json.loads(obj_path.read_text())
    data["sections"][0]["address"] = 0x0300
    obj2_path = tmp_path / "overlap2.json"
    obj2_path.write_text(json.dumps(data), encoding="utf-8")

    first = load_object(obj_path)
    second = load_object(obj2_path)
    try:
        link_objects([first, second])
    except LinkError:
        pass
    else:
        raise AssertionError("Expected overlap to raise LinkError")


def test_relocation_resolution(tmp_path):
    obj1 = _assemble_to_object(
        tmp_path,
        "modA",
        """
        .org $0300
        JSR TARGET
        BRA TARGET
        RTS
        """,
    )
    obj2 = _assemble_to_object(
        tmp_path,
        "modB",
        """
        .org $0350
TARGET: RTS
        """,
    )

    objects = [load_object(obj1), load_object(obj2)]
    result = link_objects(objects)
    assert result.symbols["TARGET"] == 0x0350
    assert [segment.address for segment in result.segments] == [0x0300, 0x0350]
    offset = (0x0300 - result.origin) + 1
    operand = (result.image[offset] << 8) | result.image[offset + 1]
    assert operand == 0x0350
    branch_offset = (0x0303 - result.origin) + 1
    rel_value = result.image[branch_offset]
    signed = rel_value if rel_value < 0x80 else rel_value - 0x100
    branch_target = 0x0303 + 2 + signed
    assert branch_target == 0x0350


def test_relative_relocation_backward(tmp_path):
    target_obj = _assemble_to_object(
        tmp_path,
        "rel_tgt",
        """
        .org $0360
TARGET: RTS
        """,
    )
    branch_obj = _assemble_to_object(
        tmp_path,
        "rel_src",
        """
        .org $0380
        BRA TARGET
        RTS
        """,
    )

    objects = [load_object(branch_obj), load_object(target_obj)]
    result = link_objects(objects)
    offset = (0x0380 - result.origin) + 1
    rel_value = result.image[offset]
    signed = rel_value if rel_value < 0x80 else rel_value - 0x100
    assert signed == -0x22

def test_relative_relocation_positive_boundary(tmp_path):
    obj = _assemble_to_object(
        tmp_path,
        "branch_forward",
        """
        .org $0300
        BRA TARGET
        .fill $7F, $00
TARGET: RTS
        """,
    )

    result = link_objects([load_object(obj)])
    offset = (0x0300 - result.origin) + 1
    rel_value = result.image[offset]
    assert rel_value == 0x7F  # +127


def test_relative_relocation_overflow(tmp_path):
    obj_branch = _assemble_to_object(
        tmp_path,
        "branch_fail",
        """
        .org $0300
        BRA TARGET
        RTS
        """,
    )

    obj_target = _assemble_to_object(
        tmp_path,
        "far_target",
        """
        .org $0500
TARGET: RTS
        """,
    )

    with pytest.raises(LinkError):
        link_objects([load_object(obj_branch), load_object(obj_target)])


def test_bss_section_zero_filled(tmp_path):
    obj_bss = _assemble_to_object(
        tmp_path,
        "bss",
        """
        .org $0400
BUFFER: .res 8
        RTS
        """,
    )
    linked = link_objects([load_object(obj_bss)])
    offset = 0x0400 - linked.origin
    assert linked.image[offset:offset + 8] == bytes([0] * 8)
    assert [segment.address for segment in linked.segments] == [0x0400]


def test_cli_link_command(tmp_path):
    obj1 = _assemble_to_object(
        tmp_path,
        "mod1",
        """
        .org $0300
LABEL1: LDAA #$11
        RTS
        """,
    )
    obj2 = _assemble_to_object(
        tmp_path,
        "mod2",
        """
        .org $0320
LABEL2: LDAA #$22
        RTS
        """,
    )

    args = SimpleNamespace(
        objects=[obj1, obj2],
        output=tmp_path / "linked.prg",
        bin=tmp_path / "linked.bin",
        map=tmp_path / "linked.map",
        entry=None,
        name="linked",
        comment="link test",
        text_base=None,
        data_base=None,
        bss_base=None,
    )
    rc = run_link(args)
    assert rc == 0
    assert args.output.exists()
    assert args.bin.exists()
    assert args.map.exists()

def test_cli_link_with_section_bases(tmp_path):
    obj = _assemble_to_object(
        tmp_path,
        "segmented",
        """
        .org $0300
        .code
        LDAA DATA
        .data
DATA:   .byte $33
        .bss
BUF:    .res 4
        """,
    )

    args = SimpleNamespace(
        objects=[obj],
        output=tmp_path / "seg.prg",
        bin=tmp_path / "seg.bin",
        map=tmp_path / "seg.map",
        entry=None,
        name="segmented",
        comment="",
        text_base=0x4000,
        data_base=0x4100,
        bss_base=0x4200,
    )
    rc = run_link(args)
    assert rc == 0
    image = (tmp_path / "seg.bin").read_bytes()
    assert image[0] == 0xB6
    assert image[0x0100] == 0x33
    symbols = {line.split(" = ")[0]: int(line.split("$")[1], 16) for line in (tmp_path / "seg.map").read_text().splitlines() if line}
    assert symbols["DATA"] == 0x4100
    assert symbols["BUF"] == 0x4200
    sections = _parse_prg_sections(args.output)
    pbin_sections = [payload for ident, payload in sections if ident == "PBIN"]
    assert len(pbin_sections) == 3
    addresses = [struct.unpack_from("<I", payload, 0)[0] for payload in pbin_sections]
    assert addresses == [0x4000, 0x4100, 0x4200]
    lengths = [struct.unpack_from("<I", payload, 4)[0] for payload in pbin_sections]
    assert lengths[0] > 0
    assert lengths[1] == 1
    assert lengths[2] == 4
    entry_comment_len = struct.unpack_from("<I", pbin_sections[0], 8 + lengths[0])[0]
    assert entry_comment_len > 0
    assert struct.unpack_from("<I", pbin_sections[1], 8 + lengths[1])[0] == 0
    assert struct.unpack_from("<I", pbin_sections[2], 8 + lengths[2])[0] == 0


def _parse_prg_sections(path):
    data = path.read_bytes()
    assert data[:4] == b"PROG"
    version = struct.unpack_from("<I", data, 4)[0]
    assert version == 2
    offset = 8
    sections = []
    while offset < len(data):
        ident = data[offset:offset + 4].decode("ascii")
        offset += 4
        length = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        payload = data[offset:offset + length]
        offset += length
        sections.append((ident, payload))
    return sections
