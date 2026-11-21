"""Rules and settings for the next Spider Escape play-test."""
from dataclasses import dataclass, field
from typing import Literal

PickupKind = Literal['ammo', 'armor', 'slow', 'repellent']
COLORS = ('original', 'blue', 'red', 'green', 'yellow')

@dataclass
class Options:
    players: int = 1
    spanish_quiz: bool = True
    colors: tuple = ('original', 'original')

    @property
    def quiz_enabled(self):
        return self.players == 1 and self.spanish_quiz

@dataclass
class CarState:
    ammo: int = 0
    effects: dict = field(default_factory=dict)

    def collect(self, kind: PickupKind, now: int):
        if kind == 'ammo':
            self.ammo += 1
        elif kind in ('armor', 'slow', 'repellent'):
            self.effects[kind] = max(now, self.effects.get(kind, now)) + 10000
        else:
            raise ValueError(f'Unknown pickup: {kind}')

    def active(self, effect: str, now: int):
        return now < self.effects.get(effect, 0)

    def fire(self):
        if not self.ammo:
            return False
        self.ammo -= 1
        return True
