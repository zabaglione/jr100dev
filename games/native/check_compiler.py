"""Check native unsigned arithmetic and short-circuiting against independent values."""

import sys
from pathlib import Path

sys.path[:0] = [
    str(Path(__file__).resolve().parents[1]),
    str(Path(__file__).resolve().parents[1] / "common"),
]
from build_game import long_branches
from checks import lib
from compiler import Compiler

from jr100dev.asm.encoder import Assembler

compiler = Compiler("""
def mark():
    s.calls += 1
    return 1

def init(): pass
def tick(): pass
def draw(): pass
def act():
    s.key = held()
    s.add = s.a + s.b
    s.sub = s.a - s.b
    s.mul = s.a * s.b
    s.div = s.a // s.b
    s.mod = s.a % s.b
    s.left = s.a << (s.b % 8)
    s.right = s.a >> (s.b % 8)
    s.mask = (s.a & s.b) ^ (s.a | s.b)
    s.calls = 0
    s.logic = (s.a < s.b and mark()) or s.a == s.b
    s.compare = (s.a > s.b) + (s.a >= s.b) + (s.a <= s.b) + (s.a != s.b)
    b[s.a % 128] = s.sub
""")
compiled = compiler.compile()
runtime = Path(__file__).with_name("runtime.asm").read_text()
helpers = runtime[runtime.index("N_INDEX:") : runtime.index("N_XY:")]
source = (
    """    .org $0300
    JSR FN_ACT
STOP:
    BRA STOP
CLOCK_SERVICE:
    RTS
MODE: .equ $3340
LEVEL: .equ $3341
ACTION: .equ $3342
KEY_LAST: .equ $3315
N_TMP: .equ $3344
N_ACC: .equ $3345
B_ARRAY: .equ $3600
"""
    + compiled
    + helpers
)
result = Assembler(long_branches(source)).assemble()
rom = bytearray(8192)
rom[:3] = bytes([0x7E, 0xE0, 0x00])
rom[-2:] = bytes([0xE0, 0])
m = lib.create(bytes(rom), len(rom))
try:
    lib.frame(m)
    for i, value in enumerate(result.machine_code):
        lib.poke(m, 0x300 + i, value)
    count = 0
    for a in (0, 1, 2, 7, 127, 128, 254, 255):
        for b in (1, 2, 3, 7, 127, 128, 255):
            for key, value in [("s.a", a), ("s.b", b)]:
                lib.poke(m, result.symbols[compiler.slots[key]], value)
            lib.poke(m, result.symbols["KEY_LAST"], a % 8)
            lib.fixture_pc(m, 0x300, 0x3FFF)
            assert lib.until(m, result.symbols["STOP"], 1_000_000), hex(lib.pc(m))
            expected = {
                "key": a % 8,
                "add": (a + b) & 255,
                "sub": (a - b) & 255,
                "mul": (a * b) & 255,
                "div": a // b,
                "mod": a % b,
                "left": (a << (b % 8)) & 255,
                "right": a >> (b % 8),
                "mask": (a & b) ^ (a | b),
                "logic": int(a <= b),
                "calls": int(a < b),
                "compare": int(a > b) + int(a >= b) + int(a <= b) + int(a != b),
            }
            for field, value in expected.items():
                actual = lib.peek(m, result.symbols[compiler.slots["s." + field]])
                assert actual == value, (a, b, field, actual, value)
            assert lib.peek(m, 0x3600 + a % 128) == (a - b) & 255
            count += 1
    assert lib.min_sp(m) >= 0x3E00
    print(
        f"PASS: {count} unsigned boundary cases, short-circuit calls and indexed stores"
    )
finally:
    lib.destroy(m)
