"""Combat and workshop fixtures verify consumed dice and persistent upgrades."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import Machine, lib
from model import State
from replay import FIELDS, choose, compare, service, settle


def fixture(s):
    m = Machine("dice_relic")
    m.action(5)
    settle(m)
    for field, name in FIELDS.items():
        lib.poke(m.p, m.sym[name], getattr(s, field))
    for name, data in [("DICE", s.dice), ("FACES", s.faces)]:
        for i, v in enumerate(data):
            lib.poke(m.p, m.sym[name] + i, v)
    return m


for s, die, choice in [
    (State(dice=[6, 4, 2], turn=1), 0, 0),
    (State(dice=[6, 4, 2], used=1, turn=1), 0, 0),
    (State(dice=[6, 4, 2], used=3, turn=1), 2, 1),
    (State(dice=[6, 4, 2], used=3, turn=4), 2, 1),
    (State(dice=[6, 4, 2], used=3, turn=4, hp=2), 2, 0),
    (State(dice=[6, 4, 2], used=3, turn=4, hp=1, enemy_hp=1), 2, 0),
    (State(dice=[6, 4, 2], hp=41, turn=1), 0, 2),
    (State(dice=[1, 1, 1], rng=128, turn=1), 1, 3),
    (State(dice=[1, 1, 1], rng=128, rerolls=0, turn=1), 1, 3),
    (State(dice=[6, 4, 2], used=3, shield=20, turn=1), 2, 0),
]:
    m = fixture(s)
    choose(m, die, choice, False)
    s.use(die, choice)
    compare(m, s)
for coins, face_value in [(2, 1), (3, 1), (3, 8), (3, 9)]:
    s = State(coins=coins, mode=2)
    s.faces[7] = face_value
    m = fixture(s)
    service(m, 1, 1, 0, True)
    s.buy(1, 1)
    if m.get("MODE") == 6:
        m.action(6)
    compare(m, s)
for hp, coins in [(42, 2), (41, 2), (30, 1), (30, 2)]:
    s = State(hp=hp, coins=coins, mode=2)
    m = fixture(s)
    service(m, 0, 0, 1, True)
    s.heal()
    if m.get("MODE") == 6:
        m.action(6)
    compare(m, s)
# Changed faces survive the next encounter and feed the real roll table.
s = State(coins=3, mode=2)
m = fixture(s)
service(m, 2, 4, 0, True)
s.buy(2, 4)
compare(m, s)
service(m, 2, 4, 2, True)
s.next_battle()
compare(m, s)
# Idle cannot spend or reroll a die, even while BGM progresses.
before = m.read("DICE", 3)
rng = m.get("RNG")
lib.ticks(m.p, 400_000)
assert m.read("DICE", 3) == before and m.get("RNG") == rng and lib.audio_peak(m.p) > 0
print(
    "PASS: attack, guard, heal, heavy attack, defeat, used dice, reroll limit, face prices/cap, healing, persistent faces, idle PCM"
)
