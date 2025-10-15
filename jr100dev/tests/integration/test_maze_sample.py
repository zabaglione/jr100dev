"""Smoke test for maze sample build.

This test invokes the (existing) Makefile to assemble/link the maze sample
project. It verifies that build artifacts (PRG/BIN/MAP) are produced in the
expected location. MAZE_SAMPLE_ROOT is based on this file's directory.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MAZE_ROOT = ROOT / "jr100dev" / "samples" / "maze"
BUILD_DIR = MAZE_ROOT / "build"


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.order("last")
def test_maze_sample_build(tmp_path):
    env = {
        "PYTHONPATH": str(ROOT),
    }
    subprocess.run(
        [
            "make",
            "build/maze.prg",
            "JR100DEV=PYTHONPATH=" + str(ROOT) + " python -m jr100dev.cli.main",
        ],
        cwd=MAZE_ROOT,
        env={**env, **{k: v for k, v in env.items()}},
        check=True,
    )
    prg = BUILD_DIR / "maze.prg"
    assert prg.exists()
    bin_path = BUILD_DIR / "maze.bin"
    assert bin_path.exists()
    map_path = BUILD_DIR / "maze.map"
    assert map_path.exists()
