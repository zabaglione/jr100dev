"""Input-only full-run acceptance; choices use only the visible hand and HUD."""

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "tests"))
from machine import Machine, lib

CARDS = json.loads((ROOT / "cards.json").read_text())
FIELDS = [
    "HP",
    "SHIELD",
    "ENERGY",
    "ENEMY_HP",
    "ENEMY_SHIELD",
    "POISON",
    "WEAK",
    "VULNERABLE",
    "STRENGTH",
    "THORNS",
    "ECHO",
    "RETAIN",
]


def state(m):
    return {key: m.get(key) for key in FIELDS}


def card_result(before, card):
    s = before.copy()
    s["ENERGY"] -= card["cost"]
    atk = card["attack"]
    if atk:
        atk += s["STRENGTH"]
        if card["special"] == 12 and s["ENEMY_HP"] <= 12:
            atk += 12
        if s["ECHO"]:
            atk *= 2
            s["ECHO"] = 0
        if s["VULNERABLE"]:
            atk += atk // 2
        absorbed = min(s["ENEMY_SHIELD"], atk)
        s["ENEMY_SHIELD"] -= absorbed
        s["ENEMY_HP"] = max(0, s["ENEMY_HP"] - (atk - absorbed))
    s["SHIELD"] = min(99, s["SHIELD"] + card["block"])
    kind, value = card["special"], card["value"]
    if kind == 1:
        s["HP"] = min(60, s["HP"] + value)
    elif kind == 2:
        s["ENERGY"] = min(9, s["ENERGY"] + value)
    elif kind == 3:
        s["POISON"] = min(99, s["POISON"] + value)
    elif kind == 4:
        s["ENERGY"] += 1
    elif kind == 5:
        s["THORNS"] += value
    elif kind == 6:
        s["VULNERABLE"] = 2
    elif kind == 7:
        s["ECHO"] = 1
    elif kind == 8:
        s["RETAIN"] = 1
    elif kind == 9:
        s["STRENGTH"] = min(20, s["STRENGTH"] + value)
    elif kind == 10:
        s["WEAK"] = 2
    return s


def invariant(m):
    deck = Counter(m.read("DECK", m.get("DECK_COUNT")))
    piles = Counter(c for c in m.read("HAND", 4) if c != 255)
    for area, count in [
        ("DRAW_PILE", "DRAW_COUNT"),
        ("DISCARD_PILE", "DISCARD_COUNT"),
        ("EXHAUST_PILE", "EXHAUST_COUNT"),
    ]:
        n = m.get(count)
        assert 0 <= n <= 24, (area, n)
        piles.update(m.read(area, n))
    assert piles == deck, (piles, deck)
    assert 0 <= m.get("HP") <= 60 and 0 <= m.get("ENERGY") <= 9
    assert 0 <= m.get("SHIELD") <= 99 and all(0 <= c < 24 for c in deck)


def select(m, index, pad=True):
    while m.get("SELECTED") != index:
        m.action(4, pad=pad)


def incoming(m):
    if m.get("INTENT") == 1:
        return 0
    return max(
        0,
        m.get("ENEMY_ATTACK")
        + (2 if m.get("INTENT") == 2 else 0)
        - (3 if m.get("WEAK") else 0),
    )


def preference(m, index, card):
    s = state(m)
    after = card_result(s, card)
    damage = s["ENEMY_HP"] - after["ENEMY_HP"]
    score = damage * 2 + (30 if after["ENEMY_HP"] == 0 else 0)
    score += min(card["block"], max(0, incoming(m) - s["SHIELD"])) * 2.5
    score += (after["HP"] - s["HP"]) * 2
    k, v = card["special"], card["value"]
    if k == 2:
        score += v * 3 if s["ENERGY"] < 5 else 0
    if k == 3:
        score += v * 3
    if k in (4, 11):
        score += 5 if s["ENERGY"] >= card["cost"] else 0
    if k == 5:
        score += v if incoming(m) else 0
    if k == 6:
        score += 2
    if k == 7:
        score += 7 if s["ENERGY"] >= 2 and not s["ECHO"] else 0
    if k == 8:
        score += 2
    if k == 9:
        score += 6 if s["ENEMY_HP"] > 18 else 0
    if k == 10:
        score += 6 if s["WEAK"] < 2 else 0
    if card["cost"] == 0:
        score += 0.1
    return score


def replay(rom=None, captures=None, pad=True):
    m = Machine("sigil_deck", rom=rom)
    if captures:
        captures.mkdir(parents=True, exist_ok=True)
        m.capture(captures / "title.png")
        m.export_workbench(captures / "title.pcg.json")
    m.action(5, pad=pad)
    invariant(m)
    steps = 0
    seen = set()
    cards_played = set()
    while m.get("MODE") not in (3, 4):
        steps += 1
        assert steps < 1200, "Run failed to terminate"
        mode = m.get("MODE")
        if mode == 2:
            fight = m.get("BATTLE") + 1
            print(f'Battle {fight:02}: WIN, HP {m.get("HP")}', flush=True)
            if captures and fight in (1, 5):
                m.capture(captures / f"reward-{fight:02}.png")
            ranks = [
                5,
                4,
                6,
                9,
                5,
                8,
                10,
                9,
                8,
                12,
                10,
                8,
                10,
                7,
                8,
                7,
                5,
                8,
                8,
                11,
                9,
                8,
                12,
                10,
            ]
            choices = list(m.read("REWARD_0", 3))
            choice = (
                3
                if m.get("HP") < 35
                else max(range(3), key=lambda i: ranks[choices[i]])
            )
            select(m, choice, pad)
            m.action(5, pad=pad)
            invariant(m)
            continue
        fight = m.get("BATTLE") + 1
        if captures and fight not in seen:
            m.capture(captures / f"battle-{fight:02}.png")
            if fight == 5:
                m.export_workbench(captures / "battle.pcg.json")
            seen.add(fight)
        hand = list(m.read("HAND", 4))
        candidates = [
            (preference(m, i, CARDS[c]), i, c)
            for i, c in enumerate(hand)
            if c != 255 and CARDS[c]["cost"] <= m.get("ENERGY")
        ]
        useful = [item for item in candidates if item[0] > 0]
        if useful:
            _, slot, card_id = max(useful)
            expected = card_result(state(m), CARDS[card_id])
            select(m, slot, pad)
            m.action(5, pad=pad)
            assert state(m) == expected, (card_id, state(m), expected)
            cards_played.add(card_id)
        else:
            select(m, 4, pad)
            m.action(5, pad=pad)
        invariant(m)
    assert m.get("MODE") == 4, f'Lost battle {m.get("BATTLE")+1}, HP {m.get("HP")}'
    assert m.read(0x300, len(m.code)) == m.code
    assert lib.min_sp(m.p) >= 0x3E00
    if captures:
        m.capture(captures / "victory.png")
    print(
        f'PASS: ten battles, HP {m.get("HP")}, {steps} decisions, {len(cards_played)} card types, SP ${lib.min_sp(m.p):04X}'
    )
    return m


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--captures", type=Path)
    parser.add_argument("--keyboard", action="store_true")
    args = parser.parse_args()
    replay(
        args.rom.read_bytes() if args.rom else None, args.captures, not args.keyboard
    )
