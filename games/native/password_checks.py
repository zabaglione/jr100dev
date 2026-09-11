"""Codec boundary fixtures plus input-only save/restart/restore on MB8861H."""

import argparse
import json
import random
from pathlib import Path

from checks import ROOT, Model, action, assert_state, begin
from machine import Machine, lib
from password import ALPHABET, KEYS, TAGS, crc, decode, encode


def raw_key(machine, row, bit, control=False, ignored=False):
    if control:
        lib.key(machine.p, 0, 0, 1)
    lib.key(machine.p, row, bit, 1)
    if ignored:
        lib.ticks(machine.p, 10000)
    else:
        machine.until("DISPATCH")
        machine.until("FRAME_READY")
    lib.key(machine.p, row, bit, 0)
    if control:
        lib.key(machine.p, 0, 0, 0)
    machine.until("INPUT_DONE")


def type_code(machine, code):
    for char in code:
        if char == " ":
            raw_key(machine, 8, 1, ignored=True)
        else:
            raw_key(machine, *KEYS[ALPHABET.index(char)])


def shown(machine):
    return "".join(ALPHABET[v] for v in machine.read("P_BUFFER", machine.get("P_LEN")))


def checked(values, tag):
    check = crc(values, tag)
    return "".join(ALPHABET[v] for v in values + [check >> 4, check & 15])


def check(name, rom=None, capture=False):
    tag = TAGS[name.replace("_", "-")]
    rng = random.Random(name)
    fixtures = [(0, bytes(40)), (39, bytes([3] * 40))]
    for prefix in (0, 1, 15, 16, 19, 20):
        for level in (0, 15, 16, 31, 32, 39):
            ratings = [3] * (prefix * 2) + [0] * (40 - prefix * 2)
            fixtures.append((level, bytes(ratings)))
            if prefix < 20:
                ratings[prefix * 2] = 2
                ratings[39] = 1
                fixtures.append((level, bytes(ratings)))
    fixtures += [
        (rng.randrange(40), bytes(rng.randrange(4) for _ in range(40)))
        for _ in range(40)
    ]
    for level, ratings in fixtures:
        code = encode(level, ratings, tag)
        assert decode(code, tag) == (level, ratings)
        for foreign in TAGS.values():
            if foreign != tag:
                try:
                    decode(code, foreign)
                except ValueError:
                    pass
                else:
                    raise AssertionError("Foreign campaign accepted")
    assert len(encode(0, bytes(40), tag)) == 4
    assert len(encode(39, bytes([3] * 40), tag)) == 5
    assert max(len(encode(i, r, tag)) for i, r in fixtures) == 24
    code = encode(39, bytes(v for i in range(20) for v in ((i % 16) >> 2, i % 4)), tag)
    corruptions = []
    for i, char in enumerate(code):
        for replacement in ALPHABET:
            if replacement != char:
                corruptions.append(code[:i] + replacement + code[i + 1 :])
        if i and char != code[i - 1]:
            corruptions.append(code[: i - 1] + char + code[i - 1] + code[i + 1 :])
    for bad in corruptions:
        try:
            decode(bad, tag)
        except ValueError:
            pass
        else:
            raise AssertionError("Character error not detected")

    # Synthetic rating fixtures exercise the codec, not gameplay completion.
    m = Machine(name)
    original = m.code
    for level, ratings in fixtures:
        lib.poke(m.p, m.sym["LEVEL"], level)
        for i, rating in enumerate(ratings):
            lib.poke(m.p, m.sym["BEST"] + i, rating)
        m.action(8 if m.get("MODE") == 0 else 6)
        assert shown(m) == encode(level, ratings, tag)
        assert m.read("BEST", 40) == ratings and m.get("LEVEL") == level
        assert m.read(0x300, len(original)) == original

    # Input, CRC/header rejection, cancel, erase and the two header variants.
    valid = [
        encode(level, ratings, tag)
        for level, ratings in fixtures[:2] + fixtures[8:12] + fixtures[-2:]
    ]
    for code in valid:
        m.action(7)
        type_code(m, " ".join(code[i : i + 4] for i in range(0, len(code), 4)))
        assert shown(m) == code
        m.action(5)
        level, ratings = decode(code, tag)
        assert m.get("MODE") == 6 and m.get("LEVEL") == level
        assert m.read("BEST", 40) == ratings
    before = (m.get("LEVEL"), m.read("BEST", 40))
    m.action(7)
    type_code(m, ALPHABET)
    assert m.read("P_BUFFER", 16) == bytes(range(16))
    m.action(7)
    bad_codes = [
        valid[-1][:i]
        + ALPHABET[(ALPHABET.index(valid[-1][i]) + 1) % 16]
        + valid[-1][i + 1 :]
        for i in (0, len(valid[-1]) // 2, len(valid[-1]) - 1)
    ]
    bad_codes += [
        "AAA",
        checked([2, 8], tag),
        checked([4, 0], tag),
        checked([8, 0], tag),
        checked([12, 0, 5], tag),
        checked([12, 0, 4, 1], tag),
        encode(5, bytes(40), next(t for t in TAGS.values() if t != tag)),
    ]
    for code in bad_codes:
        m.action(7)
        type_code(m, code)
        m.action(5)
        assert m.get("MODE") == 7 and m.get("P_ERROR") == 1
        assert (m.get("LEVEL"), m.read("BEST", 40)) == before
        m.action(7)
        assert m.get("MODE") == 6
    m.action(7)
    type_code(m, bad_codes[2])
    m.action(5)
    raw_key(m, 8, 4, control=True)
    type_code(m, valid[-1][-1])
    m.action(5)
    assert m.get("MODE") == 6 and shown(m) == valid[-1]
    m.action(7)
    type_code(m, "A" * 25)
    assert m.get("P_LEN") == 24 and m.get("P_ERROR") == 1
    m.action(7)
    assert (m.get("LEVEL"), m.read("BEST", 40)) == before

    # Generate real progress through game inputs, then restore into a fresh boot.
    old, model = begin(name, rom)
    proof = json.loads((ROOT / name / "challenges.json").read_text())[0]
    for a in proof["bonus"]:
        action(old, model, a)
    action(old, model, 5)
    action(old, model, 8, confirm=True)
    code = shown(old)
    assert decode(code, tag) == (1, bytes([3] + [0] * 39))
    fresh = Machine(name, rom=rom)
    assert fresh.read("BEST", 40) == bytes(40)
    fresh.action(7)
    type_code(fresh, code)
    if capture:
        assert rom
        fresh.capture(ROOT / name / "images/password-entry.png")
    fresh.action(5)
    assert fresh.get("MODE") == 6 and fresh.get("LEVEL") == 1
    assert fresh.read("BEST", 40) == old.read("BEST", 40)
    if capture:
        fresh.capture(ROOT / name / "images/password-restored.png")
    fresh.action(5)
    expected = Model(name)
    expected.init(1)
    expected.s.action = 5
    expected.best[:] = old.read("BEST", 40)
    assert_state(fresh, expected)
    # The one-button pad can enter and restore a full code without a keyboard.
    fresh.action(8)
    fresh.answer_reset(True)
    fresh.action(7)
    for char in code:
        while fresh.get("P_CURSOR") != ALPHABET.index(char):
            fresh.action(4, pad=True)
        fresh.action(5, pad=True)
    while fresh.get("P_CURSOR") != 16:
        fresh.action(4, pad=True)
    fresh.action(5, pad=True)
    assert fresh.get("MODE") == 6 and fresh.get("LEVEL") == 1
    assert fresh.read("BEST", 40) == old.read("BEST", 40)
    assert lib.min_sp(fresh.p) >= 0x3E00
    print(
        f"PASS: {name}, {len(fixtures)} codec fixtures, {len(corruptions)} input-error cases, rejection without writes, keyboard/pad fresh-boot restore"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game")
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    check(args.game, args.rom.read_bytes() if args.rom else None, args.capture)
