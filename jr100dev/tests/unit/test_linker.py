import json
from types import SimpleNamespace

from jr100dev.asm.encoder import Assembler
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
        .org $8000
        PART1: LDAA #1
               RTS
        """,
    )
    obj2_path = _assemble_to_object(
        tmp_path,
        "part2",
        """
        .org $8010
        PART2: LDAA #2
               RTS
        """,
    )

    objects = [load_object(obj1_path), load_object(obj2_path)]
    result = link_objects(objects)
    assert result.origin == 0x8000
    assert result.entry_point == 0x8000
    assert result.symbols["PART1"] == 0x8000
    assert result.symbols["PART2"] == 0x8010
    offset = 0x8010 - result.origin
    assert result.image[0] == 0x86
    assert result.image[offset] == 0x86


def test_link_overlap_detected(tmp_path):
    obj_path = _assemble_to_object(
        tmp_path,
        "overlap",
        """
        .org $8000
        LABEL: LDAA #1
               RTS
        """,
    )
    data = json.loads(obj_path.read_text())
    data["sections"][0]["address"] = 0x8000
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


def test_cli_link_command(tmp_path):
    obj1 = _assemble_to_object(
        tmp_path,
        "mod1",
        """
        .org $8000
LABEL1: LDAA #$11
        RTS
        """,
    )
    obj2 = _assemble_to_object(
        tmp_path,
        "mod2",
        """
        .org $8010
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
    )
    rc = run_link(args)
    assert rc == 0
    assert args.output.exists()
    assert args.bin.exists()
    assert args.map.exists()
