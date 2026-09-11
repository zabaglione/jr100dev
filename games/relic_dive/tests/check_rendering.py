"""Verify offscreen composition and single-write VRAM presentation on real CPU."""

import hashlib
import json
from pathlib import Path

from check_game import enemy, reset_room
from machine import SYMS, Machine, lib


def watch():
    lib.video_watch(SYMS["PRESENT_STORE"], SYMS["PRESENT_STORE_SECOND"])


def stats(before, after):
    changed = sum(a != b for a, b in zip(before, after))
    assert lib.video_stat(0) == changed
    assert all(lib.video_stat(i) == 0 for i in (1, 2, 3))
    return changed, lib.video_stat(4)


def check():
    # Unchanged gameplay screens from the original direct-VRAM renderer.
    # The redesigned title has separate pixel/text/bank checks in check_title.
    goldens = json.loads(Path(__file__).with_name("render_goldens.json").read_text())
    for r in goldens:
        m = Machine()
        reset_room(m)
        enemy(m, 13, 12)
        for name, value in (
            ("G_X", r["x"]),
            ("G_Y", r["y"]),
            ("G_INSPECT_X", r["x"]),
            ("G_INSPECT_Y", r["y"]),
            ("G_MODE", r["mode"]),
            ("G_MESSAGE", 0),
        ):
            m.set(name, value)
        m.call("UPDATE_VISIBILITY")
        m.call("RENDER_SCREEN")
        assert hashlib.sha256(m.read(0xC100, 768)).hexdigest() == r["sha256"], r
        m.close()
    m = Machine()
    reset_room(m)
    m.call("UPDATE_VISIBILITY")
    worst = 0
    for mode in range(10):
        m.set("G_MODE", mode)
        m.set("G_INSPECT_X", 12)
        m.set("G_INSPECT_Y", 12)
        before = m.read(0xC100, 768)
        watch()
        m.call("RENDER_FRAME")
        assert m.read(0xC100, 768) == before
        assert lib.video_stat(0) == 0
        frame = m.read("FRAMEBUFFER", 768)
        *_, cycles = m.call("PRESENT")
        assert m.read(0xC100, 768) == frame
        stats(before, frame)
        worst = max(worst, cycles)
        watch()
        m.call("RENDER_SCREEN")
        assert lib.video_stat(0) == 0, ("idle redraw", mode)
    # Worst case: every cell changes, including both bytes in every pair.
    for i in range(768):
        m.set(0xC100 + i, 255)
    before = m.read(0xC100, 768)
    watch()
    *_, cycles = m.call("PRESENT")
    assert stats(before, m.read(0xC100, 768))[0] == 768
    worst = max(worst, cycles)
    moves = []
    for x in (12, 32):
        reset_room(m)
        m.set("G_X", x)
        # Visible distant walls make scrolling alter a substantial screen area.
        for y in range(17, 29):
            for col in range(2, 62, 3):
                m.call("CELL", col, y)
                m.call("WRITE_CELL", 0)
        for i in range(SYMS["MASK_BYTES"]):
            m.set(SYMS["SEEN"] + i, 255)
        m.call("UPDATE_VISIBILITY")
        m.call("RENDER_SCREEN")
        before = m.read(0xC100, 768)
        view_before = m.get("VIEW_X")
        m.resume()
        watch()
        m.action(4, pad=True)
        assert m.get("G_X") == x + 1
        changed, span = stats(before, m.read(0xC100, 768))
        assert 0 < changed < 768
        assert (m.get("VIEW_X") != view_before) == (x == 32)
        moves.append(
            {"scroll": x == 32, "changed_cells": changed, "write_span_cycles": span}
        )
    assert lib.stack_stream_stat(1) == 0
    lib.video_watch_stop()
    m.close()
    assert worst < 35000
    return {
        "status": "passed",
        "modes": 10,
        "max_present_cycles": worst,
        "moves": moves,
    }


if __name__ == "__main__":
    print(check())
