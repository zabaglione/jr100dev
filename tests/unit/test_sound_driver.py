"""Assembler and emulator checks for the cooperative sound driver."""

from __future__ import annotations

from math import isclose
from pathlib import Path
import sys

import pytest

from jr100dev.asm.encoder import Assembler


ROOT = Path(__file__).resolve().parents[2]
EMULATOR_SRC = ROOT / "external" / "pyjr100emu" / "src"
if not EMULATOR_SRC.is_dir():
    pytest.skip("pyjr100emu checkout is required for sound runtime checks", allow_module_level=True)
if str(EMULATOR_SRC) not in sys.path:
    sys.path.insert(0, str(EMULATOR_SRC))

from jr100emu.jr100.computer import JR100Computer


def _assemble(source: str, tmp_path: Path):
    source_path = tmp_path / "sound_program.asm"
    source_path.write_text(source, encoding="utf-8")
    return Assembler(source, filename=str(source_path)).assemble()


def _run(result) -> JR100Computer:
    computer = JR100Computer(enable_audio=False)
    for offset, value in enumerate(result.machine_code):
        computer.memory.store8(result.origin + offset, value)
    computer.cpu_core.registers.program_counter = result.origin
    computer.cpu_core.registers.stack_pointer = 0x02FF
    computer.tick(100_000)
    return computer


def test_sound_driver_exports_api_and_timer_constants(tmp_path: Path) -> None:
    source = """
        .org $0300
        JMP MAIN
        .include "sound.inc"

        .data
BGM_TEST:
        .word BGM_TEST_EVENTS
        .byte 2, 0
BGM_TEST_EVENTS:
        .byte 25, 3
        .byte 0, 1
SFX_TEST:
        .byte 2
        .byte 37, 1
        .byte 0, 1

        .code
MAIN:
        JSR SOUND_INIT
        LDX #BGM_TEST
        JSR SOUND_PLAY_BGM
        JSR SOUND_TICK
        LDX #SFX_TEST
        JSR SOUND_PLAY_SFX_BLOCKING
        JSR SOUND_STOP
        RTS
    """

    result = _assemble(source, tmp_path)

    for symbol in (
        "SOUND_INIT",
        "SOUND_PLAY_BGM",
        "SOUND_TICK",
        "SOUND_PLAY_SFX_BLOCKING",
        "SOUND_STOP",
    ):
        assert symbol in result.symbols
    assert result.symbols["SOUND_VIA_T1CL"] == 0xC804
    assert result.symbols["SOUND_VIA_T1CH"] == 0xC805
    assert result.symbols["SOUND_VIA_ACR"] == 0xC80B
    assert "SOUND_VIA_IER" not in result.symbols
    assert result.machine_code


def test_sound_pitch_table_and_10ms_wait_match_the_documented_clock(tmp_path: Path) -> None:
    result = _assemble(
        """
        .org $0300
        .include "sound.inc"
        """,
        tmp_path,
    )

    table_offset = result.symbols["SOUND_NOTE_RELOADS"] - result.origin
    reloads = [
        int.from_bytes(result.machine_code[table_offset + index:table_offset + index + 2], "big")
        for index in range(0, 96, 2)
    ]
    expected = []
    for midi_note in range(48, 96):
        hertz = 440 * 2 ** ((midi_note - 69) / 12)
        expected.append(round(894_886.25 / (2 * hertz)) - 2)
    assert reloads == expected

    wait_cycles = 3 + 0x045D * (4 + 4) + 5
    assert wait_cycles == 8944
    assert isclose(wait_cycles / 894_000, 0.01000447, rel_tol=0, abs_tol=0.00000001)


def test_sound_driver_runtime_loops_rests_ends_and_resumes_after_sfx(tmp_path: Path) -> None:
    result = _assemble(
        """
        .org $0300
        JMP MAIN
        .include "sound.inc"

        .data
BGM_LOOP:
        .word BGM_LOOP_EVENTS
        .byte 3, 1
BGM_LOOP_EVENTS:
        .byte 25, 2
        .byte 0, 1
        .byte 29, 2
BGM_END:
        .word BGM_END_EVENTS
        .byte 1, $FF
BGM_END_EVENTS:
        .byte 31, 1
BGM_RESUME:
        .word BGM_RESUME_EVENTS
        .byte 1, 0
BGM_RESUME_EVENTS:
        .byte 37, 5
SFX_TEST:
        .byte 1
        .byte 45, 1

        .bss
RESULT_LOOP_PITCH: .res 1
RESULT_LOOP_REMAINING: .res 1
RESULT_LOOP_ACTIVE: .res 1
RESULT_END_ACTIVE: .res 1
RESULT_RESUME_BEFORE: .res 1
RESULT_RESUME_AFTER: .res 1
RESULT_RESUME_PITCH: .res 1
RESULT_ACR: .res 1

        .code
MAIN:
        LDS #$02FF
        JSR SOUND_INIT
        LDX #BGM_LOOP
        JSR SOUND_PLAY_BGM
        JSR SOUND_TICK
        JSR SOUND_TICK
        JSR SOUND_TICK
        JSR SOUND_TICK
        JSR SOUND_TICK
        LDAA SOUND_BGM_PITCH
        STAA RESULT_LOOP_PITCH
        LDAA SOUND_BGM_REMAINING
        STAA RESULT_LOOP_REMAINING
        LDAA SOUND_BGM_ACTIVE
        STAA RESULT_LOOP_ACTIVE

        LDX #BGM_END
        JSR SOUND_PLAY_BGM
        JSR SOUND_TICK
        LDAA SOUND_BGM_ACTIVE
        STAA RESULT_END_ACTIVE

        LDX #BGM_RESUME
        JSR SOUND_PLAY_BGM
        JSR SOUND_TICK
        LDAA SOUND_BGM_REMAINING
        STAA RESULT_RESUME_BEFORE
        LDX #SFX_TEST
        JSR SOUND_PLAY_SFX_BLOCKING
        LDAA SOUND_BGM_REMAINING
        STAA RESULT_RESUME_AFTER
        LDAA SOUND_BGM_PITCH
        STAA RESULT_RESUME_PITCH
        LDAA SOUND_VIA_ACR
        STAA RESULT_ACR
HALT:
        BRA HALT
        """,
        tmp_path,
    )
    computer = _run(result)
    memory = computer.memory
    symbol = result.symbols

    assert memory.load8(symbol["RESULT_LOOP_PITCH"]) == 0
    assert memory.load8(symbol["RESULT_LOOP_REMAINING"]) == 1
    assert memory.load8(symbol["RESULT_LOOP_ACTIVE"]) == 1
    assert memory.load8(symbol["RESULT_END_ACTIVE"]) == 0
    assert memory.load8(symbol["RESULT_RESUME_BEFORE"]) == 4
    assert memory.load8(symbol["RESULT_RESUME_AFTER"]) == 4
    assert memory.load8(symbol["RESULT_RESUME_PITCH"]) == 37
    assert memory.load8(symbol["RESULT_ACR"]) & 0xC0 == 0xC0
    assert computer.via._state.IER == 0


def test_consecutive_same_pitch_events_reload_the_bgm_event_state(tmp_path: Path) -> None:
    result = _assemble(
        """
        .org $0300
        JMP MAIN
        .include "sound.inc"

        .data
BGM_REPEAT:
        .word BGM_REPEAT_EVENTS
        .byte 3, $FF
BGM_REPEAT_EVENTS:
        .byte 25, 1
        .byte 25, 1
        .byte 0, 1

        .bss
RESULT_PITCH: .res 1
RESULT_EVENTS_LEFT: .res 1
RESULT_REMAINING: .res 1

        .code
MAIN:
        LDS #$02FF
        JSR SOUND_INIT
        LDX #BGM_REPEAT
        JSR SOUND_PLAY_BGM
        JSR SOUND_TICK
        LDAA SOUND_BGM_PITCH
        STAA RESULT_PITCH
        LDAA SOUND_BGM_EVENTS_LEFT
        STAA RESULT_EVENTS_LEFT
        LDAA SOUND_BGM_REMAINING
        STAA RESULT_REMAINING
HALT:
        BRA HALT
        """,
        tmp_path,
    )
    computer = _run(result)

    assert computer.memory.load8(result.symbols["RESULT_PITCH"]) == 25
    assert computer.memory.load8(result.symbols["RESULT_EVENTS_LEFT"]) == 1
    assert computer.memory.load8(result.symbols["RESULT_REMAINING"]) == 1
