"""Input-only nine-battle run; the policy uses visible dice and HUD values."""

import argparse
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import Machine, lib
from model import State

ROOT = Path(__file__).resolve().parent
FIELDS = {
    "hp": "HP",
    "shield": "SHIELD",
    "coins": "COINS",
    "battle": "BATTLE",
    "enemy_hp": "ENEMY_HP",
    "enemy_attack": "ENEMY_ATTACK",
    "turn": "TURN",
    "rerolls": "REROLLS",
    "used": "USED",
    "mode": "MODE",
    "rng": "RNG",
}


def settle(m):
    for _ in range(150):
        if m.get("MODE") != 7:
            m.until("IDLE")
            m.until("INPUT_DONE")
            return
        lib.frame(m.p)
    raise AssertionError("Rolling animation did not settle")


def compare(m, s):
    settle(m)
    for field, name in FIELDS.items():
        assert m.get(name) == getattr(s, field), (
            name,
            m.get(name),
            getattr(s, field),
            s,
        )
    assert list(m.read("DICE", 3)) == s.dice
    assert list(m.read("FACES", 18)) == s.faces


def choose(m, die, choice, pad):
    for _ in range((die - m.get("SELECTED")) % 3):
        m.action(4, pad)
    for _ in range((choice - m.get("CHOICE")) % 4):
        m.action(2, pad)
    m.action(5, pad)


def service(m, die, face, menu, pad):
    for _ in range((die - m.get("SELECTED")) % 3):
        m.action(4, pad)
    for _ in range((face - m.get("FACE")) % 6):
        m.action(2, pad)
    m.action(5, pad)
    for _ in range(menu):
        m.action(4, pad)
    m.action(5, pad)


def policy(s):
    unused = [i for i in range(3) if not (s.used >> i & 1)]
    smallest = min(unused, key=lambda i: s.dice[i])
    if s.rerolls and s.dice[smallest] <= 2:
        return smallest, 3
    best = None
    for assignments in itertools.product(range(3), repeat=len(unused)):
        hp = s.hp
        shield = s.shield
        damage = 0
        for i, a in zip(unused, assignments):
            if a == 0:
                damage += s.dice[i]
            elif a == 1:
                shield += s.dice[i]
            else:
                hp = min(42, hp + s.dice[i])
        attack = s.enemy_attack + (2 if s.turn % 4 == 0 else 0)
        hp_after = hp - max(0, attack - shield)
        score = (
            10000 + hp
            if damage >= s.enemy_hp
            else min(damage, s.enemy_hp) * 1.2 + hp_after * (2.1 if s.hp < 27 else 1)
        )
        if hp_after <= 0 and damage < s.enemy_hp:
            score -= 10000
        key = (score, damage, hp_after)
        if best is None or key > best[0]:
            best = (key, assignments)
    return unused[0], best[1][0]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rom", type=Path)
    p.add_argument("--capture", action="store_true")
    p.add_argument("--keyboard", action="store_true")
    args = p.parse_args()
    m = Machine("dice_relic", args.rom.read_bytes() if args.rom else None)
    pad = not args.keyboard
    if args.capture:
        assert args.rom
        (ROOT / "images").mkdir(exist_ok=True)
        (ROOT / "art").mkdir(exist_ok=True)
        m.capture(ROOT / "images/title.png")
        m.export_workbench(ROOT / "art/title.pcg.json")
    m.action(5, pad)
    settle(m)
    s = State(rng=m.get("RNG"), turn=1, dice=list(m.read("DICE", 3)))
    compare(m, s)
    steps = 0
    seen = set()
    while s.mode not in (3, 4) and steps < 1000:
        if s.mode == 2:
            if args.capture and s.battle == 3:
                m.capture(ROOT / "images/workshop.png")
                m.export_workbench(ROOT / "art/workshop.pcg.json")
            # Spend the reward on the weakest face, then carry the replacement forward.
            index = min(range(18), key=lambda i: s.faces[i])
            die, face = divmod(index, 6)
            service(m, die, face, 0, pad)
            s.buy(die, face)
            compare(m, s)
            service(m, die, face, 2, pad)
            s.next_battle()
            compare(m, s)
        if args.capture and s.battle not in seen and s.battle in (0, 8):
            m.capture(ROOT / f"images/battle-{s.battle+1:02}.png")
            seen.add(s.battle)
        die, choice = policy(s)
        choose(m, die, choice, pad)
        s.use(die, choice)
        compare(m, s)
        steps += 1
    assert s.mode == 4, (steps, s)
    assert m.read(0x300, len(m.code)) == m.code and lib.min_sp(m.p) >= 0x3E00
    if args.capture:
        m.capture(ROOT / "images/ending.png")
    print(
        f"PASS: nine battles, {steps} decisions, HP {s.hp}, 8 forged faces, SP ${lib.min_sp(m.p):04X}"
    )


if __name__ == "__main__":
    main()
