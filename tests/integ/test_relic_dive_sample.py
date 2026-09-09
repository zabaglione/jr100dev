"""Standard-RAM RELIC DIVE build and native execution contracts."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "samples/relic_dive"


def test_relic_dive_standard_ram_build():
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    subprocess.run(["make", "-C", str(SAMPLE)], env=env, check=True)
    assert (SAMPLE / "build/relic_dive.prg").is_file()
    assert (SAMPLE / "build/relic_dive.bin").stat().st_size <= 0x3000


def test_relic_dive_runtime_contracts():
    emulator = Path(os.environ.get("JR100EMU_ROOT", str(Path.home() / "jr100emu")))
    if not (emulator / "cpp/src/core.cpp").is_file():
        pytest.skip("Set JR100EMU_ROOT to the corrected JR100 emulator checkout")
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    subprocess.run(["make", "-C", str(SAMPLE)], env=env, check=True)
    subprocess.run(
        [
            sys.executable,
            str(SAMPLE / "tests/check_game.py"),
            "--seeds",
            "12",
            "--workers",
            "2",
        ],
        env=env,
        check=True,
    )
