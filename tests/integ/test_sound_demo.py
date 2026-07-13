"""Build and headless-emulator tests for the cooperative sound sample."""

from __future__ import annotations

from math import isclose
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_ROOT = ROOT / "samples" / "sound_demo"
BUILD_DIR = SAMPLE_ROOT / "build"
EMULATOR_SRC = ROOT / "external" / "pyjr100emu" / "src"
if not EMULATOR_SRC.is_dir():
    pytest.skip(
        "pyjr100emu checkout is required for sound integration checks",
        allow_module_level=True,
    )
if str(EMULATOR_SRC) not in sys.path:
    sys.path.insert(0, str(EMULATOR_SRC))

from jr100emu.jr100.computer import JR100Computer


def _build_sound_demo() -> None:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    subprocess.run(
        ["make", f"PYTHON={sys.executable}", "clean", "all"],
        cwd=SAMPLE_ROOT,
        env=env,
        check=True,
    )


def _symbols() -> dict[str, int]:
    values: dict[str, int] = {}
    for line in (BUILD_DIR / "sound_demo.map").read_text(encoding="utf-8").splitlines():
        if " = $" not in line:
            continue
        name, value = line.split(" = ", maxsplit=1)
        values[name] = int(value.removeprefix("$"), 16)
    return values


@pytest.mark.integration
def test_sound_demo_build() -> None:
    _build_sound_demo()

    assert (BUILD_DIR / "sound_demo.prg").is_file()
    assert (BUILD_DIR / "sound_demo.bin").is_file()
    assert (BUILD_DIR / "sound_demo.bin").stat().st_size < 1024
    map_text = (BUILD_DIR / "sound_demo.map").read_text(encoding="utf-8")
    assert "SOUND_INIT" in map_text
    assert "SOUND_PLAY_BGM" in map_text
    assert "SOUND_PLAY_SFX_BLOCKING" in map_text
    assert "SOUND_BGM_ODE_TO_JOY_OPENING" in map_text
    assert "SOUND_BGM_AH_VOUS_DIRAIJE_OPENING" in map_text


@pytest.mark.integration
def test_sound_demo_runs_with_timer_frequency_bgm_sfx_pcg_and_keyboard() -> None:
    _build_sound_demo()
    symbols = _symbols()
    computer = JR100Computer(enable_audio=False)
    computer.load_user_program(BUILD_DIR / "sound_demo.prg")
    computer.cpu_core.registers.program_counter = 0x0300
    computer.cpu_core.registers.stack_pointer = 0x02FF
    computer.tick(30_000)

    memory = computer.memory
    assert memory.load8(symbols["SOUND_BGM_PITCH"]) == 17
    assert memory.load8(symbols["SOUND_BGM_REMAINING"]) > 0
    assert memory.load8(0xC802) & 0xA0 == 0xA0
    assert memory.load8(0xC000) == 0x3C
    assert memory.load8(0xC180) == 0x80
    assert computer.via._state.IER == 0

    initial_hertz = 440 * 2 ** ((64 - 69) / 12)
    initial_reload = round(894_886.25 / (2 * initial_hertz)) - 2
    initial_frequency = 894_886.25 / (2 * (initial_reload + 2))
    frequencies = [
        arguments[1]
        for event, arguments in computer.hardware.sound_processor.history
        if event == "set_frequency"
    ]
    assert any(isclose(value, initial_frequency, rel_tol=0, abs_tol=0.01) for value in frequencies)

    computer.hardware.keyboard.press(0, 1)
    computer.tick(30_000)
    assert memory.load8(symbols["DEMO_LAST_ACTION"]) == 2
    assert memory.load8(symbols["SOUND_BGM_PITCH"]) == 13

    switched_hertz = 440 * 2 ** ((60 - 69) / 12)
    switched_reload = round(894_886.25 / (2 * switched_hertz)) - 2
    switched_frequency = 894_886.25 / (2 * (switched_reload + 2))
    frequencies = [
        arguments[1]
        for event, arguments in computer.hardware.sound_processor.history
        if event == "set_frequency"
    ]
    assert any(isclose(value, switched_frequency, rel_tol=0, abs_tol=0.01) for value in frequencies)

    computer.hardware.keyboard.release(0, 1)
    for _ in range(5):
        computer.tick(20_000)
        if memory.load8(symbols["DEMO_KEYS_PREVIOUS"]) == 0:
            break
    assert memory.load8(symbols["DEMO_KEYS_PREVIOUS"]) == 0

    computer.hardware.keyboard.press(0, 0)
    for _ in range(20):
        computer.tick(1_000)
        if memory.load8(symbols["DEMO_LAST_ACTION"]) == 1:
            break

    assert memory.load8(symbols["DEMO_LAST_ACTION"]) == 1
    assert memory.load8(symbols["DEMO_SFX_COUNT"]) == 0
    remaining_during_sfx = memory.load8(symbols["SOUND_BGM_REMAINING"])
    pitch_during_sfx = memory.load8(symbols["SOUND_BGM_PITCH"])
    computer.tick(1_000)
    assert memory.load8(symbols["SOUND_BGM_REMAINING"]) == remaining_during_sfx
    assert memory.load8(symbols["SOUND_BGM_PITCH"]) == pitch_during_sfx

    computer.tick(60_000)
    assert memory.load8(symbols["DEMO_SFX_COUNT"]) == 1
    assert memory.load8(symbols["SOUND_BGM_ACTIVE"]) == 1
    assert memory.load8(0xC180) == 0x81
    assert computer.via._state.IER == 0
