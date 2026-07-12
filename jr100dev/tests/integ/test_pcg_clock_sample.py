"""Build smoke test for the PCG clock sample."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
SAMPLE_ROOT = ROOT / "jr100dev" / "samples" / "pcg_clock"
BUILD_DIR = SAMPLE_ROOT / "build"


@pytest.mark.integration
def test_pcg_clock_sample_build() -> None:
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    subprocess.run(
        ["make", "clean", "all"],
        cwd=SAMPLE_ROOT,
        env=env,
        check=True,
    )

    assert (BUILD_DIR / "pcg_clock.prg").is_file()
    assert (BUILD_DIR / "pcg_clock.bin").is_file()
    map_text = (BUILD_DIR / "pcg_clock.map").read_text(encoding="utf-8")
    assert "PCG_DATA" in map_text
    assert "CLOCK_LOOP" in map_text
