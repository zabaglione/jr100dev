from jr100dev.asm.encoder import Assembler


def _assemble_with_macros(tmp_path, body: str):
    source = f"""
        .org $8000
        .include "macro.inc"
{body}
    """
    source_path = tmp_path / "program.asm"
    source_path.write_text(source, encoding="utf-8")
    assembler = Assembler(source, filename=str(source_path))
    return assembler.assemble()


def test_put_char_macro_expands(tmp_path):
    body = """
        LDX #STD_VRAM_BASE
        LDAA #'A'
        PUT_CHAR
        RTS
    """
    result = _assemble_with_macros(tmp_path, body)
    emitted = [em.line.text.strip() for em in result.emissions if em.address is not None]
    assert "STAA ,X" in emitted
    assert "INX" in emitted
    assert any(text.startswith("__STD_PRINT_STR:") and "STX STD_SRC_PTR" in text for text in emitted)
    assert result.symbols["STD_VRAM_BASE"] == 0x6000
    assert result.symbols["STD_SOUND_PORT"] == 0x2010


def test_standard_macros_runtime_support(tmp_path):
    body = """
        LDX #STD_VRAM_BASE
        LDAA #'!'
        PUT_CHAR
        PRINT_STR GREETING
        CLR_VRAM
        BEEP
        SCAN_KEY
        RTS
GREETING: .ascii "HI\\0"
    """
    result = _assemble_with_macros(tmp_path, body)
    emitted = [em.line.text.strip() for em in result.emissions if em.address is not None]
    assert "JSR __STD_PRINT_STR" in emitted
    assert "STX STD_VRAM_PTR" in emitted
    assert "JSR __STD_CLEAR_VRAM" in emitted
    assert any(text.startswith("__STD_CLEAR_VRAM:") for text in emitted)
    assert "JSR __STD_BEEP" in emitted
    assert "JSR __STD_SCAN_KEY" in emitted
    assert any(text.startswith("__STD_PRINT_DONE:") and "LDX STD_VRAM_PTR" in text for text in emitted)
    symbols = result.symbols
    assert symbols["STD_VRAM_PTR"] == 0x00F0
    assert symbols["STD_SRC_PTR"] == 0x00F2
    assert "__STD_PRINT_STR" in symbols
    assert "__STD_CLEAR_VRAM" in symbols
