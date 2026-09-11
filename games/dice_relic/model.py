"""Independent combat rules, including persistent face values and PRNG."""

import json
from dataclasses import dataclass, field
from pathlib import Path

ENEMIES = json.loads(Path(__file__).with_name("enemies.json").read_text())


@dataclass
class State:
    hp: int = 42
    shield: int = 0
    coins: int = 0
    battle: int = 0
    enemy_hp: int = 14
    enemy_attack: int = 3
    turn: int = 0
    rerolls: int = 1
    used: int = 0
    mode: int = 1
    rng: int = 1
    dice: list = field(default_factory=lambda: [0] * 3)
    faces: list = field(default_factory=lambda: [1, 2, 3, 4, 5, 6] * 3)

    def roll(self, index):
        self.rng = ((self.rng << 1) ^ (0x1D if self.rng & 128 else 0)) & 255
        self.dice[index] = self.faces[index * 6 + self.rng % 6]

    def new_turn(self):
        self.turn = (self.turn + 1) % 256
        self.used = 0
        self.rerolls = 1
        for i in range(3):
            self.roll(i)

    def next_battle(self):
        self.battle += 1
        e = ENEMIES[self.battle]
        self.enemy_hp = e["hp"]
        self.enemy_attack = e["attack"]
        self.turn = 0
        self.shield = 0
        self.mode = 1
        self.new_turn()

    def use(self, i, choice):
        if self.used >> i & 1:
            return
        if choice == 3:
            if self.rerolls:
                self.rerolls -= 1
                self.roll(i)
            return
        value = self.dice[i]
        self.used |= 1 << i
        if choice == 0:
            self.enemy_hp = max(0, self.enemy_hp - value)
            if not self.enemy_hp:
                self.hp = min(42, self.hp + 2)
                self.coins += 3
                self.mode = 4 if self.battle == 8 else 2
                return
        elif choice == 1:
            self.shield += value
        else:
            self.hp = min(42, self.hp + value)
        if self.used == 7:
            attack = self.enemy_attack + (2 if self.turn % 4 == 0 else 0)
            self.hp = max(0, self.hp - max(0, attack - self.shield))
            if not self.hp:
                self.mode = 3
                return
            self.shield = 0
            self.new_turn()

    def buy(self, die, face):
        index = die * 6 + face
        if self.coins >= 3 and self.faces[index] < 9:
            self.coins -= 3
            self.faces[index] = min(9, self.faces[index] + 2)

    def heal(self):
        if self.coins >= 2 and self.hp < 42:
            self.coins -= 2
            self.hp = min(42, self.hp + 6)
