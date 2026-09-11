"""Play a real Frost Steps clear; hold input through the audible result pause."""

import json

from machine import KEYS, Machine, lib


def check():
    m = Machine("frost_steps")
    route = json.loads((m.directory / "solutions.json").read_text())[0]
    m.action(5)
    for a in route[:-1]:
        m.action(a)
    last = route[-1]
    lib.audio_peak(m.p)
    lib.key(m.p, *KEYS[last], 1)
    m.until("DISPATCH")
    m.until("RESULT_LISTEN")
    assert m.get("MODE") == 2 and m.get("RESULT_ACTIVE") == 1
    lib.key(m.p, *KEYS[last], 0)
    screen = m.read(0xC100, 768)
    began = lib.clocks(m.p)
    finished = None
    notes = set()
    for frame in range(130):
        if frame == 8:
            lib.key(m.p, *KEYS[6], 1)
        if frame == 14:
            lib.key(m.p, *KEYS[6], 0)
        if frame == 20:
            lib.key(m.p, *KEYS[5], 1)
        lib.frame(m.p)
        notes.add(m.get("SOUND_LAST"))
        assert m.get("MODE") == 2 and m.get("LEVEL") == 0
        assert m.read(0xC100, 768) == screen, "Final board was erased or skipped"
        assert m.get("CN_ACTIVE") == 0, "Buffered SPACE opened a reset"
        if finished is None and not m.get("RESULT_ACTIVE"):
            finished = lib.clocks(m.p)
    seconds = (finished - began) / 894886.25
    assert 1.5 < seconds < 2.1, seconds
    assert len(notes - {0}) >= 4 and lib.audio_peak(m.p) > 0
    assert m.get("SOUND_LAST") == 0 and m.get("KEY_PENDING") == 0
    lib.key(m.p, *KEYS[5], 0)
    # Frame sampling can stop halfway through a matrix scan. Observe the
    # release rather than assuming its first remaining row already saw it.
    for _ in range(3):
        lib.frame(m.p)
    assert m.get("KEY_LAST") == 0
    m.action(5)
    assert m.get("MODE") == 1 and m.get("LEVEL") == 1
    assert m.read(0x300, len(m.code)) == m.code
    assert lib.min_sp(m.p) >= 0x3E00
    print(
        f"PASS: real clear, {seconds:.2f}s stable result, melody/PCM, no buffered skip, fresh Return advances"
    )


if __name__ == "__main__":
    check()
