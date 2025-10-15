#!/usr/bin/env python3
"""Smoke checks for maze test cartridges using the local jr100 emulator."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


REPO_ROOT = Path(__file__).resolve().parents[4]
PYJR100EMU_SRC = REPO_ROOT / "external" / "pyjr100emu" / "src"

if str(PYJR100EMU_SRC) not in sys.path:
    sys.path.insert(0, str(PYJR100EMU_SRC))

from jr100emu.debug_runner import (  # type: ignore  # pylint: disable=wrong-import-position
    _execute_program,
    _initialise_cpu_state,
    _load_program,
    _setup_computer,
)


TEST_DIR = Path(__file__).resolve().parent
MAZE_SAMPLE_DIR = TEST_DIR.parent
MAZE_SAMPLE_BUILD = MAZE_SAMPLE_DIR / "build"
CELL_VISITED_FLAG = 0x10


@dataclass(frozen=True)
class MemoryExpectation:
    base: int
    values: Sequence[int]

    def verify(self, memory) -> None:
        for offset, expected in enumerate(self.values):
            actual = memory.load8(self.base + offset) & 0xFF
            if actual != expected:
                raise AssertionError(
                    f"addr=0x{self.base + offset:04X}: expected 0x{expected:02X}, got 0x{actual:02X}"
                )


def build_prg(target: str) -> Path:
    prg_path = TEST_DIR / "build" / f"{target}.prg"
    if not prg_path.exists():
        raise FileNotFoundError(prg_path)
    return prg_path


def run_cartridge(prg_path: Path, *, seconds: float = 1.0) -> object:
    computer = _setup_computer(None)
    _load_program(computer, str(prg_path))
    _initialise_cpu_state(computer, start_address=0x0300, stack_pointer=0x0244)
    _execute_program(
        computer,
        max_cycles=None,
        breakpoints=[],
        max_seconds=seconds,
    )
    return computer.memory


def ensure_maze_sample() -> Path:
    prg_path = MAZE_SAMPLE_BUILD / "maze.prg"
    if not prg_path.exists():
        subprocess.run(["make", "build/maze.prg"], cwd=MAZE_SAMPLE_DIR, check=True)
    return prg_path


def load_symbol_map() -> Dict[str, int]:
    symbol_map: Dict[str, int] = {}
    map_path = MAZE_SAMPLE_BUILD / "maze.map"
    with map_path.open(encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if "=" not in line:
                continue
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip().split()[0]
            if value.startswith("$"):
                symbol_map[name] = int(value[1:], 16)
    return symbol_map


def run_maze_generation(level_index: int, seconds: float) -> object:
    prg_path = ensure_maze_sample()
    symbols = load_symbol_map()
    required = ("MAZE_APPLY_LEVEL", "MAZE_GENERATE", "MENU_SELECTED")
    missing = [name for name in required if name not in symbols]
    if missing:
        raise RuntimeError(f"Missing symbol(s) in maze.map: {', '.join(missing)}")

    computer = _setup_computer(None)
    _load_program(computer, str(prg_path))
    memory = computer.memory
    memory.store8(symbols["MENU_SELECTED"], level_index & 0xFF)

    _initialise_cpu_state(computer, start_address=symbols["MAZE_APPLY_LEVEL"], stack_pointer=0x0244)
    if computer.cpu_core is None:
        raise RuntimeError("CPU core is unavailable")
    computer.cpu_core.registers.acc_a = level_index & 0xFF
    _execute_program(
        computer,
        max_cycles=2000,
        breakpoints=[],
        max_seconds=None,
    )

    _initialise_cpu_state(computer, start_address=symbols["MAZE_GENERATE"], stack_pointer=0x0244)
    _execute_program(
        computer,
        max_cycles=None,
        breakpoints=[],
        max_seconds=seconds,
    )
    return memory


def check_maze_init() -> None:
    prg = build_prg("maze_init_test")
    memory = run_cartridge(prg)
    maze_base = 0x0600
    width = 11
    height = 11
    top_row = MemoryExpectation(maze_base, [0x23] * width)
    inner_left = MemoryExpectation(maze_base + width, [0x23])
    inner_body = MemoryExpectation(maze_base + width + 1, [0x20] * (width - 2))
    inner_right = MemoryExpectation(maze_base + width + (width - 1), [0x23])
    bottom_row = MemoryExpectation(maze_base + width * (height - 1), [0x23] * width)
    for expectation in (top_row, inner_left, inner_body, inner_right, bottom_row):
        expectation.verify(memory)
    print("maze_init_test: OK")


def check_maze_step() -> None:
    prg = build_prg("maze_step_test")
    memory = run_cartridge(prg)
    vram_expected = MemoryExpectation(0xC100, [0x03, 0x40, 0x40, 0x40])
    vram_expected.verify(memory)
    print("maze_step_test: OK")


def check_maze_stack() -> None:
    prg = build_prg("maze_stack_test")
    memory = run_cartridge(prg)
    expectations = [
        MemoryExpectation(0x0500, [0x01, 0x02, 0x03, 0x04]),
        MemoryExpectation(0x0600, [0x01, 0x01, 0x03, 0x04, 0x01, 0x03, 0x04, 0x01]),
        MemoryExpectation(0x0608, [0x05, 0x00, 0x05, 0x00, 0x05, 0x04, 0x05, 0x02, 0x05, 0x00, 0x01, 0x02]),
        MemoryExpectation(0x0614, [0x01, 0x05, 0x00]),
    ]
    for expectation in expectations:
        expectation.verify(memory)
    print("maze_stack_test: OK")


def check_maze_neighbors() -> None:
    prg = build_prg("maze_neighbors_test")
    memory = run_cartridge(prg)
    expectations = [
        MemoryExpectation(0x0600, [0x02, 0x01, 0x03, 0xEE, 0xEE]),
        MemoryExpectation(0x0605, [0x02, 0x01, 0x02, 0xEE, 0xEE]),
        MemoryExpectation(0x060A, [0x00, 0xEE, 0xEE, 0xEE, 0xEE]),
        MemoryExpectation(0x0610, [0x00, 0x01, 0x01, 0x02]),
        MemoryExpectation(0x0614, [0x01, 0x00, 0x01, 0x00]),
        MemoryExpectation(0x0618, [0x01, 0x01, 0x00, 0x00]),
    ]
    for expectation in expectations:
        expectation.verify(memory)
    print("maze_neighbors_test: OK")


def check_maze_wall_mark() -> None:
    prg = build_prg("maze_wall_mark_test")
    memory = run_cartridge(prg)
    expectation = MemoryExpectation(0x0600, [0x0B, 0x0E, 0x01, 0x01, 0x07, 0x0D, 0x01, 0x01])
    expectation.verify(memory)
    print("maze_wall_mark_test: OK")


def check_maze_carve() -> None:
    prg = build_prg("maze_carve_test")
    memory = run_cartridge(prg)
    expectation = MemoryExpectation(0x3800, [0x20, 0x23, 0x20, 0x20, 0x20, 0x23, 0x20, 0x20, 0x20, 0x23])
    expectation.verify(memory)
    print("maze_carve_test: OK")


def check_maze_scroll() -> None:
    prg = build_prg("maze_scroll_test")
    memory = run_cartridge(prg)
    base = 0x0900
    expected = {
        0: 5,   # origin_x (case 1)
        1: 3,   # origin_y (case 1)
        2: 2,   # draw_x (case 1)
        3: 7,   # draw_y (case 1)
        4: 2,   # origin_x after left clamp
        5: 4,   # draw_x after left clamp
        6: 4,   # origin_x after right scroll
        7: 8,   # draw_x after right scroll
        8: 18,  # origin_y when clamped at max
        9: 22,  # draw_y when clamped at max
        10: 1,  # origin_y after top scroll
        11: 3,  # draw_y after top scroll
    }
    for offset, value in expected.items():
        actual = memory.load8(base + offset) & 0xFF
        if actual != value:
            raise AssertionError(
                f"maze_scroll_test: offset {offset:#04x} expected {value:#04x}, got {actual:#04x}"
            )
    print("maze_scroll_test: OK")


CHECKERS: Dict[str, callable] = {
    "maze_init_test": check_maze_init,
    "maze_step_test": check_maze_step,
    "maze_stack_test": check_maze_stack,
    "maze_neighbors_test": check_maze_neighbors,
    "maze_wall_mark_test": check_maze_wall_mark,
    "maze_carve_test": check_maze_carve,
    "maze_scroll_test": check_maze_scroll,
}


def check_maze_level(level_index: int, expected_width: int, expected_height: int, label: str) -> None:
    seconds = 30.0 if expected_width >= 32 else 2.0
    memory = run_maze_generation(level_index, seconds=seconds)

    width = memory.load8(0x0600)
    height = memory.load8(0x0601)
    if width != expected_width or height != expected_height:
        raise AssertionError(f"{label}: expected size {expected_width}x{expected_height}, got {width}x{height}")

    symbols = load_symbol_map()
    maze_base = symbols["MAZE_MAP"]
    cell_w = memory.load8(0x0602)
    cell_h = memory.load8(0x0603)
    top = [memory.load8(maze_base + col) & 0xFF for col in range(width)]
    bottom_base = maze_base + width * (height - 1)
    bottom = [memory.load8(bottom_base + col) & 0xFF for col in range(width)]
    if any(value != 0x23 for value in top):
        raise AssertionError(f"{label}: top border is not sealed")
    if any(value != 0x23 for value in bottom):
        raise AssertionError(f"{label}: bottom border is not sealed")

    inner_paths = 0
    for row in range(1, height - 1):
        row_base = maze_base + row * width
        for col in range(1, width - 1):
            if memory.load8(row_base + col) & 0xFF == 0x20:
                inner_paths += 1
    if inner_paths == 0:
        raise AssertionError(f"{label}: no passages carved in maze interior")

    visited_base = symbols["VISITED_MAP"]
    expected_cells = cell_w * cell_h
    visited_count = sum(
        1
        for index in range(expected_cells)
        if (memory.load8(visited_base + index) & 0xFF) == CELL_VISITED_FLAG
    )
    if visited_count / max(expected_cells, 1) < 0.9:
        raise AssertionError(
            f"{label}: insufficient cells visited ({visited_count}/{expected_cells})"
        )

    print(f"{label}: OK")


def check_maze_sample_easy() -> None:
    check_maze_level(0, 11, 11, "maze_sample_easy")


def check_maze_sample_normal() -> None:
    check_maze_level(1, 21, 21, "maze_sample_normal")


def check_maze_sample_hard() -> None:
    check_maze_level(2, 41, 41, "maze_sample_hard")


CHECKERS.update(
    {
        "maze_sample_easy": check_maze_sample_easy,
        "maze_sample_normal": check_maze_sample_normal,
    }
)


def main() -> None:
    targets: List[str]
    if len(sys.argv) > 1:
        targets = sys.argv[1:]
    else:
        targets = list(CHECKERS.keys())

    unknown = [name for name in targets if name not in CHECKERS]
    if unknown:
        raise SystemExit(f"Unknown test name(s): {', '.join(unknown)}")

    for name in targets:
        CHECKERS[name]()


if __name__ == "__main__":
    main()
