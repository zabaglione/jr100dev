import json
from types import SimpleNamespace

from jr100dev.asm.encoder import Assembler
from jr100dev.cli.main import run_assemble


def assemble(source: str):
    assembler = Assembler(source, filename="test.asm")
    return assembler.assemble()


def test_simple_program():
    source = """
        .org $8000
        START: LDAA #$41
               STAA $6000
               RTS
    """
    result = assemble(source)
    assert result.origin == 0x8000
    assert result.entry_point == 0x8000
    assert result.machine_code == bytes([0x86, 0x41, 0xB7, 0x60, 0x00, 0x39])
    assert result.symbols["START"] == 0x8000


def test_direct_and_extended_addressing():
    source = """
        .org $8000
        LDAA FWD
        LDAA $80
        LDAA >$80
        LDAA $1234
SMALL:  .equ $0020
        LDAA <SMALL
FWD:    .equ $00FF
        LDAA <FWD
        RTS
    """
    result = assemble(source)
    expected = bytes(
        [
            0x96,
            0xFF,  # LDAA FWD -> direct after forward symbol resolution
            0x96,
            0x80,
            0xB6,
            0x00,
            0x80,
            0xB6,
            0x12,
            0x34,
            0x96,
            0x20,
            0x96,
            0xFF,
            0x39,
        ]
    )
    assert result.machine_code == expected
    assert result.symbols["SMALL"] == 0x0020
    assert result.symbols["FWD"] == 0x00FF


def test_object_dict_structure():
    source = """
        .org $8000
LABEL:  LDAA #1
        RTS
    """
    assembler = Assembler(source, filename="sample.asm")
    result = assembler.assemble()
    obj = result.to_object_dict()
    assert obj["format"] == "jr100dev-object"
    assert obj["origin"] == 0x8000
    assert obj["entry_point"] == 0x8000
    assert obj["source"].endswith("sample.asm")
    assert obj["symbols"][0]["name"] == "LABEL"
    assert obj["sections"][0]["content"] == "860139"


def test_object_dict_relocations():
    source = """
        .org $8000
        LDAA <EXTBUF
        BRA EXTENTRY
        RTS
    """
    assembler = Assembler(source, filename="reloc.asm")
    result = assembler.assemble()
    relocations = result.to_object_dict()["relocations"]
    assert {
        (reloc["target"], reloc["type"])
        for reloc in relocations
    } == {("EXTBUF", "absolute8"), ("EXTENTRY", "relative8")}


def test_object_dict_bss_section():
    source = """
        .org $8000
BUFFER: .res 4
        RTS
    """
    assembler = Assembler(source, filename="bss.asm")
    result = assembler.assemble()
    obj = result.to_object_dict()
    bss_sections = [s for s in obj["sections"] if s["kind"] == "bss"]
    assert bss_sections[0]["bss_size"] == 4
    assert bss_sections[0]["content"] == ""


def test_object_dict_data_section():
    source = """
        .org $8000
        .data
CONST:  .byte $AA, $55
        .code
        RTS
    """
    assembler = Assembler(source, filename="data.asm")
    result = assembler.assemble()
    obj = result.to_object_dict()
    data_sections = [s for s in obj["sections"] if s["kind"] == "data"]
    assert data_sections[0]["content"] == "AA55"
    assert result.symbols["CONST"] == 0x8000


def test_cli_object_output(tmp_path):
    src = tmp_path / "prog.asm"
    src.write_text(
        """
        .org $8000
START:  LDAA #$42
        RTS
        """
    )
    obj_path = tmp_path / "prog.json"
    args = SimpleNamespace(
        source=src,
        output=tmp_path / "prog.prg",
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
    data = json.loads(obj_path.read_text())
    assert data["origin"] == 0x8000
    assert data["sections"][0]["content"].startswith("86")
    assert (tmp_path / "prog.bin").exists()
    assert args.output.exists()
