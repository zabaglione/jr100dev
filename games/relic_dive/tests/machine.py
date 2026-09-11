"""Execute the actual MB8861H program in the corrected native JR100 core."""

import ctypes as C
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMU = Path(os.environ.get("JR100EMU_ROOT", str(Path.home() / "jr100emu")))
LIB = ROOT / "build/emulator_bridge.dylib"
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
            str(LIB.with_suffix(".tmp")),
        ],
        check=True,
    )
    LIB.with_suffix(".tmp").replace(LIB)
lib = C.CDLL(str(LIB))
for name, args, ret in [
    ("stack_stream_range", [C.c_int, C.c_int, C.c_int], None),
    ("stack_stream_stat", [C.c_int], C.c_int),
    ("video_watch", [C.c_int, C.c_int], None),
    ("video_stat", [C.c_int], C.c_longlong),
    ("video_watch_stop", [], None),
    ("create", [C.c_void_p, C.c_int], C.c_void_p),
    ("destroy", [C.c_void_p], None),
    ("poke", [C.c_void_p, C.c_int, C.c_int], None),
    ("peek", [C.c_void_p, C.c_int], C.c_int),
    ("read_bytes", [C.c_void_p, C.c_int, C.c_void_p, C.c_int], None),
    ("registers_set", [C.c_void_p] + [C.c_int] * 5, None),
    ("reg", [C.c_void_p, C.c_int], C.c_int),
    ("clocks", [C.c_void_p], C.c_longlong),
    ("run_until", [C.c_void_p, C.c_int, C.c_int], C.c_int),
    ("key", [C.c_void_p] + [C.c_int] * 3, None),
    ("pad", [C.c_void_p, C.c_int], None),
    ("snapshot", [C.c_void_p], C.c_void_p),
    ("restore", [C.c_void_p, C.c_void_p], None),
    ("snapshot_free", [C.c_void_p], None),
    ("pixels", [C.c_void_p, C.c_void_p], None),
    ("headless_search", [C.c_int, C.c_int], None),
    ("mutations", [], C.c_ulonglong),
    ("headless_search_enabled", [], C.c_int),
    ("min_sp", [], C.c_int),
    ("reset_min_sp", [], None),
]:
    f = getattr(lib, name)
    f.argtypes = args
    f.restype = ret
SYMS = {
    k: int(v, 16)
    for k, v in re.findall(
        r"^(\w+)\s*=\s*\$([0-9A-Fa-f]+)",
        (ROOT / "build/relic-dive.map").read_text(),
        re.MULTILINE,
    )
}
lib.stack_stream_range(
    SYMS["PRESENT_STREAM_BEGIN"], SYMS["PRESENT_RESTORE"], SYMS["FRAMEBUFFER"]
)
KEYS = {
    1: (2, 1),
    2: (0, 3),
    3: (1, 0),
    4: (1, 2),
    5: (8, 3),
    6: (8, 1),
    7: (2, 0),
    8: (2, 2),
    9: (0, 2),
    10: (0, 4),
    11: (1, 1),
}

PADS = {1: 4, 2: 8, 3: 2, 4: 1, 5: 16, 7: 6, 8: 5, 9: 10, 10: 9}


class Machine:
    def __init__(self, rom=None):
        data = rom or bytes(8192)
        self.p = lib.create(data, len(data))
        self.code = (ROOT / "build/relic-dive.bin").read_bytes()
        for i, b in enumerate(self.code):
            lib.poke(self.p, 0x300 + i, b)
        lib.registers_set(self.p, 0x300, 0x244, 0, 0, 0)
        self.until("FRAME_READY")
        self.call("POLL_KEY")

    def close(self):
        if self.p:
            lib.destroy(self.p)
            self.p = None

    def __del__(self):
        self.close()

    def addr(self, k):
        return SYMS[k] if isinstance(k, str) else k

    def get(self, k):
        return lib.peek(self.p, self.addr(k))

    def set(self, k, v):
        lib.poke(self.p, self.addr(k), v)

    def word(self, k):
        return self.get(k) * 256 + self.get(self.addr(k) + 1)

    def setw(self, k, v):
        self.set(k, v >> 8)
        self.set(self.addr(k) + 1, v & 255)

    def read(self, k, n):
        out = C.create_string_buffer(n)
        lib.read_bytes(self.p, self.addr(k), out, n)
        return out.raw

    def until(self, label, limit=30_000_000):
        start = lib.clocks(self.p)
        ok = lib.run_until(self.p, self.addr(label), limit)
        if not ok:
            pc = lib.reg(self.p, 0)
            near = max((v, k) for k, v in SYMS.items() if v <= pc)
            raise AssertionError(
                f'timeout pc={pc:04x} near={near} mode={self.get("G_MODE")} floor={self.get("G_FLOOR")}'
            )
        return lib.clocks(self.p) - start

    def call(self, name, a=0, b=0, ix=0):
        # Isolated routine fixtures only. Input replays do not use this method.
        self.set(0x3FFE, 2)
        self.set(0x3FFF, 0x80)
        lib.registers_set(self.p, self.addr(name), 0x3FFD, a, b, ix)
        c = self.until(0x280)
        return lib.reg(self.p, 2), lib.reg(self.p, 3), lib.reg(self.p, 4), c

    def resume(self):
        lib.registers_set(self.p, SYMS["FRAME_READY"], 0x3FFF, 0, 0, 0)

    def action(self, n, pad=False):
        if pad:
            lib.pad(self.p, PADS[n])
        else:
            lib.key(self.p, *KEYS[n], 1)
        c = self.until("DISPATCH")
        c += self.until("FRAME_READY")
        if pad:
            lib.pad(self.p, 0)
        else:
            lib.key(self.p, *KEYS[n], 0)
        # Run to the end of a poll to observe release, keeping the real stack.
        self.until("POLL_DONE")
        return c

    def start(self, difficulty=1):
        self.resume()
        if difficulty == 0:
            self.action(1)
        if difficulty == 2:
            self.action(2)
        return self.action(5)

    def map(self):
        data = self.read("FLOORS", SYMS["TERRAIN_BYTES"])
        return [v for b in data for v in (b & 15, b >> 4)]

    def entities(self):
        raw = self.read(SYMS["FLOORS"] + SYMS["ENEMY_START"], 256)
        return [list(raw[i : i + 8]) for i in range(0, 256, 8)]

    def items(self):
        raw = self.read(SYMS["FLOORS"] + SYMS["ITEM_START"], 96)
        return [list(raw[i : i + 3]) for i in range(0, 96, 3)]
