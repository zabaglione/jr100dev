"""Native-core test harness; published frames require a user-owned ROM."""

import ctypes as C
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMU = Path(os.environ.get("JR100EMU_ROOT", str(Path.home() / "jr100emu")))
BUILD = ROOT / "build"
BUILD.mkdir(exist_ok=True)
LIB = BUILD / "emulator_bridge.dylib"
SOURCES = [Path(__file__).with_name("emulator_bridge.cpp")] + [
    EMU / "cpp/src" / n for n in ("core.cpp", "cpu.cpp", "via.cpp")
]
if not LIB.exists() or any(p.stat().st_mtime > LIB.stat().st_mtime for p in SOURCES):
    subprocess.run(
        [
            "c++",
            "-std=c++20",
            "-O2",
            "-shared",
            "-fPIC",
            "-I" + str(EMU / "cpp/include"),
            "-I" + str(EMU / "cpp/src"),
            *map(str, SOURCES),
            "-o",
            str(LIB),
        ],
        check=True,
    )
lib = C.CDLL(str(LIB))
for name, args, result in [
    ("create", [C.c_void_p, C.c_int], C.c_void_p),
    ("destroy", [C.c_void_p], None),
    ("peek", [C.c_void_p, C.c_int], C.c_int),
    ("poke", [C.c_void_p, C.c_int, C.c_int], None),
    ("fixture_pc", [C.c_void_p, C.c_int, C.c_int], None),
    ("reset_stats", [C.c_void_p], None),
    ("pc", [C.c_void_p], C.c_int),
    ("min_sp", [C.c_void_p], C.c_int),
    ("clocks", [C.c_void_p], C.c_longlong),
    ("until", [C.c_void_p, C.c_int, C.c_int], C.c_int),
    ("ticks", [C.c_void_p, C.c_int], None),
    ("until_either", [C.c_void_p, C.c_int, C.c_int, C.c_int], C.c_int),
    ("frame", [C.c_void_p], None),
    ("load_prg", [C.c_void_p, C.c_void_p, C.c_int], C.c_int),
    ("key", [C.c_void_p] + [C.c_int] * 3, None),
    ("pad", [C.c_void_p, C.c_int], None),
    ("pixels", [C.c_void_p, C.c_void_p], None),
    ("audio_peak", [C.c_void_p], C.c_int),
]:
    f = getattr(lib, name)
    f.argtypes, f.restype = args, result

KEYS = {
    1: (2, 1),
    2: (1, 1),
    3: (1, 0),
    4: (1, 2),
    5: (8, 3),
    6: (8, 1),
    7: (0, 3),
    8: (1, 3),
}
PADS = {1: 4, 2: 8, 3: 2, 4: 1, 5: 16, 9: 6, 10: 5, 11: 10, 12: 9}
EIGHT_KEYS = KEYS | {2: (0, 3), 9: (2, 0), 10: (2, 2), 11: (0, 2), 12: (0, 4)}


class Machine:
    def __init__(self, game="chrono_breach", rom=None):
        self.directory = ROOT / game
        self.metadata = json.loads((self.directory / "game.json").read_text())
        self.sym = json.loads((self.directory / "build/symbols.json").read_text())
        self.code = (
            self.directory / "build" / f'{game.replace("_", "-")}.bin'
        ).read_bytes()
        if rom:
            self.p = lib.create(rom, len(rom))
            for _ in range(100):
                lib.frame(self.p)
            data = (
                self.directory / "build" / f'{game.replace("_", "-")}.prg'
            ).read_bytes()
            assert lib.load_prg(self.p, data, len(data))
            # The genuine BASIC ROM consumes the core's automatic USR command.
            for _ in range(500):
                lib.frame(self.p)
                if 0x300 <= lib.pc(self.p) < self.sym["CODE_END"]:
                    break
            else:
                raise AssertionError("BASIC autostart did not enter the game")
            self.until("FRAME_READY")
            # Finish the final automatic Return release without injecting input.
            for _ in range(10):
                lib.frame(self.p)
        else:
            dummy = bytearray(8192)
            dummy[0:3] = bytes([0x7E, 0xE0, 0x00])
            dummy[-2:] = bytes([0xE0, 0])
            self.p = lib.create(bytes(dummy), len(dummy))
            lib.frame(self.p)
            for i, v in enumerate(self.code):
                lib.poke(self.p, 0x300 + i, v)
            lib.fixture_pc(self.p, 0x300, 0x244)
            self.until("FRAME_READY")
        self.until("INPUT_DONE")
        assert self.get("MODE") == 0
        lib.reset_stats(self.p)

    def __del__(self):
        if getattr(self, "p", None):
            lib.destroy(self.p)
            self.p = None

    def get(self, name):
        return lib.peek(self.p, self.sym[name] if isinstance(name, str) else name)

    def read(self, name, length):
        address = self.sym[name] if isinstance(name, str) else name
        return bytes(self.get(address + i) for i in range(length))

    def until(self, name, budget=3_000_000):
        address = self.sym[name] if isinstance(name, str) else name
        before = lib.clocks(self.p)
        assert lib.until(
            self.p, address, budget
        ), f"timeout {name}: pc={lib.pc(self.p):04x}"
        return lib.clocks(self.p) - before

    def action(self, action, pad=False):
        keys = EIGHT_KEYS if self.metadata.get("directions") == 8 else KEYS
        if pad:
            lib.pad(self.p, PADS[action])
        else:
            lib.key(self.p, *keys[action], 1)
        self.until("DISPATCH")
        self.until("FRAME_READY")
        if pad:
            lib.pad(self.p, 0)
        else:
            lib.key(self.p, *keys[action], 0)
        self.until("INPUT_DONE")

    def capture(self, filename):
        from PIL import Image, ImageOps

        buffer = C.create_string_buffer(256 * 192)
        lib.pixels(self.p, buffer)
        raw = bytes(255 if p else 0 for p in buffer.raw)
        image = Image.frombytes("L", (256, 192), raw).resize(
            (768, 576), Image.Resampling.NEAREST
        )
        ImageOps.expand(image, border=24, fill=0).save(filename)

    def export_workbench(self, filename):
        bank = self.read(0xC000, 256)
        project = {
            "version": 3,
            "name": f"{self.metadata['title']} - {filename.stem}",
            "glyphs": [list(bank[i : i + 8]) for i in range(0, 256, 8)],
            "names": [f"Tile {i:02}" for i in range(32)],
            "groups": [],
            "animations": [],
            "screen": {"mode": "pcg", "cells": list(self.read(0xC100, 768))},
        }
        # Omitting romGlyphs makes the editor supply its built-in approximation.
        filename.write_text(json.dumps(project, indent=2) + "\n")
