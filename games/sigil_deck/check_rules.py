"""Explicit battle fixtures for all cards, conservation and effect boundaries."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import Machine, lib
from replay import CARDS, card_result, invariant, select, state


def put(m, key, value):
    lib.poke(m.p, m.sym[key] if isinstance(key, str) else key, value)


def fixture(card_id=0, **changes):
    m = Machine("sigil_deck")
    m.action(5)
    values = {
        "HP": 31,
        "SHIELD": 7,
        "ENERGY": 3,
        "ENEMY_HP": 80,
        "ENEMY_SHIELD": 5,
        "POISON": 4,
        "WEAK": 1,
        "VULNERABLE": 1,
        "STRENGTH": 2,
        "THORNS": 3,
        "ECHO": 1,
        "RETAIN": 0,
        "DECK_COUNT": 4,
        "DRAW_COUNT": 3,
        "DISCARD_COUNT": 0,
        "EXHAUST_COUNT": 0,
        "SELECTED": 0,
        "INTENT": 0,
    }
    values.update(changes)
    for key, value in values.items():
        put(m, key, value)
    for i, value in enumerate([card_id, 0, 1, 2]):
        put(m, m.sym["DECK"] + i, value)
    for i, value in enumerate([0, 1, 2]):
        put(m, m.sym["DRAW_PILE"] + i, value)
    for i in range(4):
        put(m, m.sym["HAND"] + i, card_id if i == 0 else 255)
    return m


for card_id, card in enumerate(CARDS):
    m = fixture(card_id)
    expected = card_result(state(m), card)
    m.action(5)
    assert state(m) == expected, (card_id, state(m), expected)
    invariant(m)
    assert m.get("EXHAUST_COUNT") == card["exhaust"]
    assert m.get("DISCARD_COUNT") == 1 - card["exhaust"]
    expected_draw = 1 if card["special"] == 4 else 2 if card["special"] == 11 else 0
    assert sum(c != 255 for c in m.read("HAND", 4)) == expected_draw
    if card["special"] in (4, 11):
        assert card_id not in m.read("HAND", 4), "Resolving card redrawn"
print("PASS: all 24 card effects, cost, exhaust and draw conservation")

m = fixture(20, ENERGY=2)
before = state(m)
hand = m.read("HAND", 4)
m.action(5)
assert state(m) == before and m.read("HAND", 4) == hand
m = fixture(21, SHIELD=98)
m.action(5)
assert m.get("SHIELD") == 99
m = fixture(19, HP=59)
m.action(5)
assert m.get("HP") == 60
m = fixture(15, STRENGTH=19)
m.action(5)
assert m.get("STRENGTH") == 20
m = fixture(22, POISON=98)
m.action(5)
assert m.get("POISON") == 99
for hp, expected in ((12, 0), (13, 9)):
    m = fixture(23, ENEMY_HP=hp, ENEMY_SHIELD=0, STRENGTH=0, VULNERABLE=0, ECHO=0)
    m.action(5)
    assert m.get("ENEMY_HP") == expected
print("PASS: insufficient energy, stat caps and finisher threshold")

for intent in range(3):
    for retain in (0, 1):
        m = fixture(INTENT=intent, RETAIN=retain)
        before = state(m)
        expected = before.copy()
        expected["ENEMY_SHIELD"] = 0
        expected["ENEMY_HP"] -= expected["POISON"]
        expected["POISON"] -= 1
        if intent == 1:
            expected["ENEMY_SHIELD"] = m.get("ENEMY_GUARD")
        else:
            incoming = max(0, m.get("ENEMY_ATTACK") + (2 if intent == 2 else 0) - 3)
            absorbed = min(expected["SHIELD"], incoming)
            expected["SHIELD"] -= absorbed
            expected["HP"] -= incoming - absorbed
            expected["ENEMY_HP"] -= expected["THORNS"]
        expected["WEAK"] -= 1
        expected["VULNERABLE"] -= 1
        if not retain:
            expected["SHIELD"] = 0
        expected["THORNS"] = 0
        expected["RETAIN"] = 0
        expected["ENERGY"] = 3
        select(m, 4)
        m.action(5)
        assert state(m) == expected, (intent, retain, state(m), expected)
        invariant(m)
print("PASS: enemy intents, shield expiry, retain, poison, thorns and status durations")

m = fixture(0, ENEMY_HP=1, ENEMY_SHIELD=0, HP=10, SHIELD=0, POISON=0, THORNS=1, WEAK=0)
put(m, "ENEMY_ATTACK", 20)
select(m, 4)
m.action(5)
assert m.get("MODE") == 3 and m.get("HP") == 0 and m.get("ENEMY_HP") == 0
m.action(5, pad=True)
m.answer_reset(True, pad=True)
assert m.get("MODE") == 1 and m.get("HP") == 60 and m.get("DECK_COUNT") == 8
# Poison can win before the enemy's attack; resting heals and advances a battle.
m = fixture(0, ENEMY_HP=1, POISON=1, HP=1, SHIELD=0, WEAK=0)
select(m, 4)
m.action(5)
assert m.get("MODE") == 2 and m.get("HP") == 1
select(m, 3)
m.action(5)
assert m.get("HP") == 15 and m.get("BATTLE") == 1
# Exhaust is battle-local and every master-deck card returns for a new fight.
m = fixture(18, ENEMY_HP=1, POISON=1, HP=40)
m.action(5)
assert m.get("EXHAUST_COUNT") == 1
select(m, 4)
m.action(5)
assert m.get("MODE") == 2
select(m, 3)
m.action(5)
assert m.get("EXHAUST_COUNT") == 0
invariant(m)
print("PASS: simultaneous defeat, retry, poison victory, rest and exhaust reset")
