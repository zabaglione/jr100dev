"""Build smoke test for the PCG animation sample."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_ROOT = ROOT / "samples" / "pcg_animation"
BUILD_DIR = SAMPLE_ROOT / "build"


@pytest.mark.integration
def test_pcg_animation_sample_build() -> None:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    subprocess.run(
        ["make", "clean", "all"],
        cwd=SAMPLE_ROOT,
        env=env,
        check=True,
    )

    assert (BUILD_DIR / "pcg_animation.prg").is_file()
    assert (BUILD_DIR / "pcg_animation.bin").is_file()
    map_text = (BUILD_DIR / "pcg_animation.map").read_text(encoding="utf-8")
    assert "ANIM_APPLY_FRAME" in map_text
    assert "PLAYER_LEFT_0" in map_text
    assert "PLAYER_FRAME_POINTERS" in map_text
