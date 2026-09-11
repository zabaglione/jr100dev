"""Capture native-core frames during a saved input replay (requires owned ROM)."""

import argparse
import ctypes
import json
import struct
import zlib
from pathlib import Path

from machine import EMU, ROOT, SYMS, Machine, lib


def capture(machine, name):
    pixels = ctypes.create_string_buffer(256 * 192)
    lib.pixels(machine.p, pixels)

    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data))
        )

    raw = b"".join(
        b"\0"
        + bytes(
            255 if value else 0
            for value in pixels.raw[y * 256 : (y + 1) * 256]
            for _ in range(3)
        )
        for y in range(192)
        for _ in range(3)
    )
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 768, 576, 8, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )
    (ROOT / "build" / f"{name}.png").write_bytes(png)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, default=EMU / "datas/jr100rom.prg")
    args = parser.parse_args()
    machine = Machine(args.rom.read_bytes())
    capture(machine, "title")
    machine.start(0)
    plan = json.loads(
        Path(__file__).with_name("replays").joinpath("easy.json").read_text()
    )
    captured = set()
    cameras = set()
    for index, action in enumerate(plan["inputs"]):
        machine.action(action, pad=action not in (6, 11))
        mode = machine.get("G_MODE")
        if mode not in captured:
            capture(machine, f"mode-{mode}")
            captured.add(mode)
        camera = (machine.get("VIEW_X"), machine.get("VIEW_Y"))
        if (
            mode == 1
            and camera not in cameras
            and camera[0] in (0, SYMS["MAP_WIDTH"] - 32)
            and camera[1] in (0, 12)
        ):
            capture(machine, f"camera-{camera[0]}-{camera[1]}")
            cameras.add(camera)
        if index == 150:
            capture(machine, "gameplay")
    machine.close()


if __name__ == "__main__":
    main()
