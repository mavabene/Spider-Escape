"""Rules and settings for the next Spider Escape play-test."""
from dataclasses import dataclass, field
from typing import Literal

PickupKind = Literal['ammo', 'armor', 'slow', 'repellent', 'flame']
COLORS = ('original', 'blue', 'red', 'green', 'yellow')
FLAME_FUEL_MS = 2000

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
    flame_fuel: int = 0
    flame_capacity: int = FLAME_FUEL_MS

    def collect(self, kind: PickupKind, now: int):
        if kind == 'ammo':
            self.ammo += 1
        elif kind == 'flame':
            self.flame_fuel += FLAME_FUEL_MS
            self.flame_capacity = max(self.flame_capacity, self.flame_fuel)
        elif kind in ('armor', 'slow', 'repellent'):
            self.effects[kind] = max(now, self.effects.get(kind, now)) + 10000
        else:
            raise ValueError(f'Unknown pickup: {kind}')

    def active(self, effect: str, now: int):
        return now < self.effects.get(effect, 0)

    def armor_visible(self, now: int):
        remaining = self.effects.get('armor', 0) - now
        if remaining <= 0:
            return False
        return remaining > 3000 or ((3000 - remaining) // 250) % 2 == 0

    def armor_color(self, now: int):
        blue = (100, 210, 255)
        red = (255, 55, 45)
        remaining = self.effects.get('armor', 0) - now
        blend = max(0.0, min(1.0, 1 - remaining / 5000))
        return tuple(round(start + (end - start) * blend) for start, end in zip(blue, red))

    def fire(self):
        if not self.ammo:
            return False
        self.ammo -= 1
        return True

    def use_flame(self, elapsed_ms):
        if not self.flame_fuel:
            return False
        self.flame_fuel = max(0, self.flame_fuel - elapsed_ms)
        return True
